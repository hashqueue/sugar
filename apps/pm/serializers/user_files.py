from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

from pm.models import UserFile
from system.models import User
from utils.drf_utils.base_model_serializer import BaseModelSerializer


class UserFileCreateUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = UserFile
        fields = '__all__'
        read_only_fields = ('id', 'create_time', 'update_time', 'creator', 'modifier')


class UserFileRetrieveSerializer(BaseModelSerializer):
    creator_name = serializers.SerializerMethodField(help_text='创建人姓名')
    file_name = serializers.SerializerMethodField(help_text='文件名称')

    class Meta:
        model = UserFile
        fields = '__all__'

    @extend_schema_field(OpenApiTypes.STR)
    def get_creator_name(self, obj: UserFile):
        return User.objects.filter(username=obj.creator).first().name

    @extend_schema_field(OpenApiTypes.STR)
    def get_file_name(self, obj: UserFile):
        return obj.file.name
