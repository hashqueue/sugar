from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema
from django_filters import rest_framework as filters

from utils.drf_utils.custom_json_response import JsonResponse, unite_response_format_schema
from task.serializers.task_results import TaskResultCreateUpdateSerializer, TaskResultRetrieveSerializer
from task.models import TaskResult


class TaskResultFilter(filters.FilterSet):
    device_id = filters.NumberFilter(field_name='device', label='所属设备ID')

    class Meta:
        model = TaskResult
        fields = ['device_id', 'task_status']


@extend_schema(tags=['任务执行结果管理'])
class TaskResultViewSet(ModelViewSet):
    queryset = TaskResult.objects.all().order_by('-create_time')
    filterset_class = TaskResultFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TaskResultCreateUpdateSerializer
        elif self.action in ['retrieve', 'destroy', 'list']:
            return TaskResultRetrieveSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user.username, modifier=self.request.user.username)

    def perform_update(self, serializer):
        serializer.save(modifier=self.request.user.username)

    @extend_schema(responses=unite_response_format_schema('create-task-result', TaskResultCreateUpdateSerializer))
    def create(self, request, *args, **kwargs):
        """
        create task-result
        """
        res = super().create(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_201_CREATED,
                            headers=res.headers)

    def list(self, request, *args, **kwargs):
        """
        select task-result list
        """
        res = super().list(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_200_OK)

    @extend_schema(responses=unite_response_format_schema('select-task-result-detail', TaskResultRetrieveSerializer))
    def retrieve(self, request, *args, **kwargs):
        """
        select task-result detail
        """
        res = super().retrieve(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_200_OK)

    @extend_schema(
        responses=unite_response_format_schema('update-task-result-detail', TaskResultCreateUpdateSerializer))
    def update(self, request, *args, **kwargs):
        """
        update task-result detail
        """
        res = super().update(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000)

    @extend_schema(
        responses=unite_response_format_schema('partial-update-task-result-detail', TaskResultCreateUpdateSerializer))
    def partial_update(self, request, *args, **kwargs):
        """
        partial update task-result detail
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        delete task-result
        """
        return super().destroy(request, *args, **kwargs)
