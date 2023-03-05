import json

from django.core.cache import cache
from django.shortcuts import get_object_or_404
from rest_framework import status, serializers
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from django_filters import rest_framework as filters
from django_celery_beat.models import PeriodicTask, IntervalSchedule

from utils.drf_utils.custom_json_response import JsonResponse, unite_response_format_schema
from device.serializers.devices import DeviceCreateUpdateSerializer, DeviceRetrieveSerializer, \
    GetDeviceAliveLogSerializer, CreateCollectDevicePerfDataTaskSerializer
from device.models import Device
from task.models import TaskResult
from task.serializers.task_results import TaskResultRetrieveSerializer
from utils.base.publish_mq_msg import publish_message
from sugar.settings import TASK_CHECK_DEVICE_STATUS_TIME, env
from device.tasks import deploy_agent_to_device


class DeviceFilter(filters.FilterSet):
    host = filters.CharFilter(field_name='host', lookup_expr='icontains', label='域名或IP(模糊搜索且不区分大小写)')
    username = filters.CharFilter(field_name='username', lookup_expr='icontains',
                                  label='用户名(模糊搜索且不区分大小写)')

    class Meta:
        model = Device
        fields = ['host', 'username', 'device_type', 'device_status']


@extend_schema(tags=['设备管理'])
class DeviceViewSet(ModelViewSet):
    queryset = Device.objects.all().order_by('-id')
    filterset_class = DeviceFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return DeviceCreateUpdateSerializer
        elif self.action in ['retrieve', 'destroy', 'list']:
            return DeviceRetrieveSerializer
        elif self.action in ['collect_device_perf_data']:
            return CreateCollectDevicePerfDataTaskSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user.username, modifier=self.request.user.username)
        data = serializer.data
        # 注册设备探活定时任务
        schedule, created = IntervalSchedule.objects.get_or_create(every=int(TASK_CHECK_DEVICE_STATUS_TIME),
                                                                   period=IntervalSchedule.SECONDS, )
        PeriodicTask.objects.create(
            interval=schedule,  # we created this above.
            name=f'{data.get("id")}_check_device_status',  # simply describes this periodic task.
            task='device.tasks.check_device_status',  # name of task.
            kwargs=json.dumps({'host': data.get('host'), 'username': data.get('username'),
                               'password': data.get('password'), 'port': data.get('port'),
                               'device_id': data.get('id')})
        )

    def perform_update(self, serializer):
        serializer.save(modifier=self.request.user.username)
        data = serializer.data
        # 更新设备探活定时任务参数
        task = PeriodicTask.objects.filter(name__startswith=str(data.get("id"))).first()
        if task:
            task.kwargs = json.dumps({'host': data.get('host'), 'username': data.get('username'),
                                      'password': data.get('password'), 'port': data.get('port'),
                                      'device_id': data.get('id')})
            task.last_run_at = None
            task.save()

    def perform_destroy(self, instance):
        # 删除设备探活定时任务
        task = PeriodicTask.objects.filter(name__startswith=str(instance.id)).first()
        if task:
            task.enabled = False
            task.last_run_at = None
            task.save()
            task.delete()
        instance.delete()

    @extend_schema(responses=unite_response_format_schema('create-device', DeviceCreateUpdateSerializer))
    def create(self, request, *args, **kwargs):
        """
        create device

        @`device_status` = [(0, '离线'), (1, '在线')]


        @`device_type` = [(0, '阿里云ECS'), (1, '腾讯云ECS'), (2, 'Raspberry Pi(树莓派)')]
        """
        res = super().create(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_201_CREATED,
                            headers=res.headers)

    def list(self, request, *args, **kwargs):
        """
        select device list
        """
        res = super().list(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_200_OK)

    @extend_schema(responses=unite_response_format_schema('select-device-detail', DeviceRetrieveSerializer))
    def retrieve(self, request, *args, **kwargs):
        """
        select device detail
        """
        res = super().retrieve(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_200_OK)

    @extend_schema(
        responses=unite_response_format_schema('update-device-detail', DeviceCreateUpdateSerializer))
    def update(self, request, *args, **kwargs):
        """
        update device detail
        """
        res = super().update(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000)

    @extend_schema(
        responses=unite_response_format_schema('partial-update-device-detail',
                                               DeviceCreateUpdateSerializer))
    def partial_update(self, request, *args, **kwargs):
        """
        partial update device detail
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        delete device
        """
        return super().destroy(request, *args, **kwargs)

    @extend_schema(responses=unite_response_format_schema('get-device-alive-logs', GetDeviceAliveLogSerializer))
    @action(methods=['get'], detail=True, url_path='device-alive-logs')
    def get_device_check_alive_log(self, request, pk=None, version=None):
        get_object_or_404(Device, pk=pk)
        device_cache_keys = cache.keys(f'{pk}_*')
        if device_cache_keys:
            cache_datas = cache.get_many(device_cache_keys)
            results = [{float(key.split('_')[-1]): json.loads(value)} for key, value in cache_datas.items()]
            # 根据时间戳进行排序
            results.sort(key=lambda x: list(x.keys())[0], reverse=True)
            return JsonResponse({"results": [list(item.values())[0] for item in results]}, msg='success', code=20000)
        return JsonResponse({"results": []}, msg='success', code=20000)

    @extend_schema(
        responses=unite_response_format_schema('collect-device-perf-data', TaskResultRetrieveSerializer))
    @action(methods=['post'], detail=True, url_path='collect-perf-data')
    def collect_device_perf_data(self, request, pk=None, version=None):
        """
        采集设备某个时间段内的性能数据
        """
        create_task_serializer = CreateCollectDevicePerfDataTaskSerializer(data=request.data)
        device_status = Device.objects.filter(pk=pk).values_list('device_status', flat=True).first()
        if create_task_serializer.is_valid(raise_exception=True):
            if device_status == 0:
                raise serializers.ValidationError('设备离线，无法采集性能数据', code=40000)
            task = TaskResult.objects.create(task_status=0, task_type=0, device_id=pk,
                                             creator=self.request.user.username,
                                             modifier=self.request.user.username)
            message = {"task_type": 0,
                       "metadata": {
                           "base_url": env("TASK_HTTP_CALLBACK_BASE_URL"), "task_id": str(task.task_id),
                           "username": env("TASK_HTTP_CALLBACK_USERNAME"),
                           "password": env("TASK_HTTP_CALLBACK_PASSWORD"),
                           "task_config": {"intervals": create_task_serializer.data.get('intervals'),
                                           "count": create_task_serializer.data.get('count')}
                       }}
            try:
                publish_message(env('RABBITMQ_USER'), env('RABBITMQ_PASSWORD'), env('RABBITMQ_HOST'),
                                env('RABBITMQ_PORT'), 'device_exchange', 'device_perf_data',
                                json.dumps(message, ensure_ascii=False))
            except Exception as e:
                raise serializers.ValidationError(f'发送消息到消息队列失败, {e}', code=40000)
            TaskResult.objects.filter(task_id=task.task_id).update(metadata=message)
            task_result_serializer = TaskResultRetrieveSerializer(instance=task)
            return JsonResponse(data=task_result_serializer.data,
                                msg='采集设备性能数据任务已启动, 请在采集历史中查看数据详情.', code=20000)

    @extend_schema(
        responses=unite_response_format_schema('deploy-agent-to-device', TaskResultRetrieveSerializer))
    @action(methods=['get'], detail=True, url_path='deploy-agent')
    def deploy_agent_to_device(self, request, pk=None, version=None):
        """
        部署agent到目标服务器中并启动agent
        """
        device_status = Device.objects.filter(pk=pk).values_list('device_status', flat=True).first()
        if device_status == 0:
            raise serializers.ValidationError('设备离线，无法部署agent', code=40000)
        task = TaskResult.objects.create(task_status=0, task_type=1, device_id=pk,
                                         creator=self.request.user.username,
                                         modifier=self.request.user.username)
        message = {"task_type": 1,
                   "metadata": {
                       "base_url": env("TASK_HTTP_CALLBACK_BASE_URL"), "task_id": str(task.task_id),
                       "username": env("TASK_HTTP_CALLBACK_USERNAME"),
                       "password": env("TASK_HTTP_CALLBACK_PASSWORD"),
                       "task_config": Device.objects.filter(pk=pk).values('username', 'password', 'host',
                                                                          'port').first()
                   }}
        TaskResult.objects.filter(task_id=task.task_id).update(metadata=message)
        config = message['metadata']['task_config']
        # start deploy agent to device
        deploy_agent_to_device.delay(host=config['host'], username=config['username'], password=config['password'],
                                     port=config['port'], task_id=str(task.task_id))
        task_result_serializer = TaskResultRetrieveSerializer(instance=task)
        return JsonResponse(data=task_result_serializer.data,
                            msg='已开始向设备中部署agent, 请在日志中查看部署进度.', code=20000)
