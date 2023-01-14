from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

from pm.models import Sprint
from system.models import User
from utils.drf_utils.base_model_serializer import BaseModelSerializer


class SprintCreateUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = Sprint
        fields = '__all__'
        read_only_fields = ('id', 'create_time', 'update_time', 'creator', 'modifier')


class SprintRetrieveSerializer(BaseModelSerializer):
    start_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True, help_text='开始时间')
    finish_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True, help_text='完成时间')
    owner_name = serializers.SerializerMethodField(help_text='负责人姓名')
    project_name = serializers.CharField(source='project.name', help_text='所属套件的名称')
    feature_count = serializers.SerializerMethodField(help_text='需求数量')
    task_count = serializers.SerializerMethodField(help_text='任务数量')
    bug_count = serializers.SerializerMethodField(help_text='缺陷数量')

    class Meta:
        model = Sprint
        fields = '__all__'

    @extend_schema_field(OpenApiTypes.STR)
    def get_owner_name(self, obj: Sprint):
        return User.objects.filter(username=obj.owner).first().name

    @extend_schema_field(OpenApiTypes.INT)
    def get_feature_count(self, obj: Sprint):
        return obj.workitem_set.filter(type=0).count()

    @extend_schema_field(OpenApiTypes.INT)
    def get_task_count(self, obj: Sprint):
        return obj.workitem_set.filter(type=1).count()

    @extend_schema_field(OpenApiTypes.INT)
    def get_bug_count(self, obj: Sprint):
        return obj.workitem_set.filter(type=2).count()
