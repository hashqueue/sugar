from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

from pm.models import WorkItem
from system.models import User
from utils.drf_utils.base_model_serializer import BaseModelSerializer


class WorkItemCreateUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = WorkItem
        fields = '__all__'
        read_only_fields = ('id', 'create_time', 'update_time', 'creator', 'modifier')


class WorkItemRetrieveSerializer(BaseModelSerializer):
    deadline = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True, help_text='截止日期')
    owner_name = serializers.SerializerMethodField(help_text='负责人姓名')
    sprint_name = serializers.CharField(source='sprint.name', help_text='所属迭代的名称')

    class Meta:
        model = WorkItem
        fields = '__all__'

    @extend_schema_field(OpenApiTypes.STR)
    def get_owner_name(self, obj: WorkItem):
        return User.objects.filter(username=obj.owner).first().name
