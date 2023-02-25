import json

from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema
from django_filters import rest_framework as filters
from django_celery_beat.models import PeriodicTask, IntervalSchedule

from utils.drf_utils.custom_json_response import JsonResponse, unite_response_format_schema
from device.serializers.devices import DeviceCreateUpdateSerializer, DeviceRetrieveSerializer
from device.models import Device
from sugar.settings import CHECK_DEVICE_ALIVE_TIME


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

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user.username, modifier=self.request.user.username)
        data = serializer.data
        # 注册设备探活定时任务
        schedule, created = IntervalSchedule.objects.get_or_create(every=int(CHECK_DEVICE_ALIVE_TIME),
                                                                   period=IntervalSchedule.SECONDS, )
        PeriodicTask.objects.create(
            interval=schedule,  # we created this above.
            name=f'{data.get("id")}_check_device_is_alive',  # simply describes this periodic task.
            task='device.tasks.check_device_is_alive',  # name of task.
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
            task.save()

    def perform_destroy(self, instance):
        # 删除设备探活定时任务
        task = PeriodicTask.objects.filter(name__startswith=str(instance.id)).first()
        if task:
            task.enabled = False
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
