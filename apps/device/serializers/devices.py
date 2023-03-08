from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

from system.models import User
from device.models import Device
from utils.drf_utils.base_model_serializer import BaseModelSerializer


class DeviceCreateUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'
        read_only_fields = ('id', 'create_time', 'update_time', 'creator', 'modifier', 'device_status')

    # def create(self, validated_data):
    #     result, msg = check_device_ssh_available(validated_data.get('host'), validated_data.get('username'),
    #                                              validated_data.get('password'), validated_data.get('port'))
    #     if result:
    #         validated_data['device_status'] = 1
    #     else:
    #         validated_data['device_status'] = 0
    #     device = Device.objects.create(**validated_data)
    #     return device
    #
    # def update(self, instance, validated_data):
    #     instance.username = validated_data.get('username', instance.username)
    #     instance.password = validated_data.get('password', instance.password)
    #     instance.host = validated_data.get('host', instance.host)
    #     instance.port = validated_data.get('port', instance.port)
    #     instance.device_type = validated_data.get('device_type', instance.device_type)
    #
    #     result, msg = check_device_ssh_available(validated_data.get('host'), validated_data.get('username'),
    #                                              validated_data.get('password'), validated_data.get('port'))
    #     if result:
    #         instance.device_status = 1
    #     else:
    #         instance.device_status = 0
    #     instance.save()
    #     return instance


class DeviceRetrieveSerializer(BaseModelSerializer):
    creator_name = serializers.SerializerMethodField(help_text='创建人姓名')
    modifier_name = serializers.SerializerMethodField(help_text='最后修改人姓名')

    class Meta:
        model = Device
        fields = '__all__'

    @extend_schema_field(OpenApiTypes.STR)
    def get_creator_name(self, obj: Device):
        return User.objects.filter(username=obj.creator).first().name

    @extend_schema_field(OpenApiTypes.STR)
    def get_modifier_name(self, obj: Device):
        return User.objects.filter(username=obj.modifier).first().name


class DeviceAliveLogTaskResultSerializer(serializers.Serializer):
    result = serializers.BooleanField(help_text='任务运行结果')
    msg = serializers.CharField(help_text='任务运行结果详情')


class DeviceAliveLogKwargsSerializer(serializers.Serializer):
    host = serializers.CharField(help_text='设备IP或域名')
    username = serializers.CharField(help_text='设备用户名')
    port = serializers.IntegerField(help_text='设备端口')
    device_id = serializers.IntegerField(help_text='设备ID')


class DeviceAliveLogSerializer(serializers.Serializer):
    task_id = serializers.CharField(help_text='任务ID')
    task_status = serializers.CharField(help_text='任务状态')
    args = serializers.ListField(child=serializers.CharField(), help_text='任务位置参数')
    kwargs = DeviceAliveLogKwargsSerializer(help_text='任务关键字参数')
    error = serializers.CharField(help_text='任务异常信息', allow_null=True)
    task_result = DeviceAliveLogTaskResultSerializer(help_text='任务执行结果', allow_null=True)
    complete_time = serializers.DateTimeField(help_text='任务完成时间')


class GetDeviceAliveLogSerializer(serializers.Serializer):
    # 无需定义Meta class，直接继承自Serializer class，适合于自定义接口的返回值格式的场景
    results = DeviceAliveLogSerializer(many=True, help_text='设备探活日志列表')


class CreateCollectDevicePerfDataTaskSerializer(serializers.Serializer):
    intervals = serializers.IntegerField(min_value=1, help_text='间隔时间(秒)')
    count = serializers.IntegerField(min_value=1, help_text='采集次数')
