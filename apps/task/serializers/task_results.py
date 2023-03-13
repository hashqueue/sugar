from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

from system.models import User
from task.models import TaskResult
from utils.drf_utils.base_model_serializer import BaseModelSerializer


class TaskResultCreateUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = TaskResult
        fields = '__all__'
        read_only_fields = ('id', 'create_time', 'update_time', 'creator', 'modifier')


class TaskResultRetrieveSerializer(BaseModelSerializer):
    creator_name = serializers.SerializerMethodField(help_text='创建人姓名')
    time_duration = serializers.SerializerMethodField(help_text='任务耗时')

    class Meta:
        model = TaskResult
        fields = '__all__'

    @extend_schema_field(OpenApiTypes.STR)
    def get_creator_name(self, obj: TaskResult):
        return User.objects.filter(username=obj.creator).first().name

    @extend_schema_field(OpenApiTypes.STR)
    def get_time_duration(self, obj: TaskResult):
        if obj.create_time and obj.update_time:
            time_duration = obj.update_time - obj.create_time
            days = time_duration.days
            hours = time_duration.seconds // 3600
            minutes = (time_duration.seconds - hours * 3600) // 60
            seconds = time_duration.seconds - hours * 3600 - minutes * 60
            return f'{days}天{hours}小时{minutes}分钟{seconds}秒'
        else:
            return ''
