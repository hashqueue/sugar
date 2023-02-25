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
