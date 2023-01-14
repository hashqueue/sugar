from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

from system.models import User
from pm.models import Project
from system.serializers.users import UserThinRetrieveSerializer
from utils.drf_utils.base_model_serializer import BaseModelSerializer


class ProjectCreateUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ('id', 'create_time', 'update_time', 'creator', 'modifier')


class ProjectRetrieveSerializer(BaseModelSerializer):
    members = UserThinRetrieveSerializer(many=True, read_only=True, help_text='项目成员')
    owner_name = serializers.SerializerMethodField(help_text='负责人姓名')
    sprint_count = serializers.SerializerMethodField(help_text='迭代数量')

    class Meta:
        model = Project
        fields = '__all__'

    @extend_schema_field(OpenApiTypes.STR)
    def get_owner_name(self, obj: Project):
        return User.objects.filter(username=obj.owner).first().name

    @extend_schema_field(OpenApiTypes.INT)
    def get_sprint_count(self, obj: Project):
        return obj.sprint_set.count()
