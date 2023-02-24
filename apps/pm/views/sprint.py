from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema
from django_filters import rest_framework as filters

from utils.drf_utils.custom_json_response import JsonResponse, unite_response_format_schema
from pm.serializers.sprints import SprintCreateUpdateSerializer, SprintRetrieveSerializer
from pm.models import Sprint


class SprintFilter(filters.FilterSet):
    owner = filters.CharFilter(field_name='owner', lookup_expr='icontains', label='负责人(模糊搜索且不区分大小写)')
    name = filters.CharFilter(field_name='name', lookup_expr='icontains', label='迭代名称(模糊搜索且不区分大小写)')
    creator = filters.CharFilter(field_name='creator', lookup_expr='icontains', label='创建人(模糊搜索且不区分大小写)')
    project_id = filters.NumberFilter(field_name='project', label='所属项目ID')

    class Meta:
        model = Sprint
        fields = ['project_id', 'name', 'sprint_status', 'owner', 'creator']


@extend_schema(tags=['迭代管理'])
class SprintViewSet(ModelViewSet):
    queryset = Sprint.objects.all().order_by('-id')
    filterset_class = SprintFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SprintCreateUpdateSerializer
        elif self.action in ['retrieve', 'destroy', 'list']:
            return SprintRetrieveSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user.username, modifier=self.request.user.username)

    def perform_update(self, serializer):
        serializer.save(modifier=self.request.user.username)

    @extend_schema(responses=unite_response_format_schema('create-sprint', SprintCreateUpdateSerializer))
    def create(self, request, *args, **kwargs):
        """
        create sprint

        @`sprint_status` = [(0, '未开始'), (1, '进行中'), (2, '已完成')]
        """
        res = super().create(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_201_CREATED,
                            headers=res.headers)

    def list(self, request, *args, **kwargs):
        """
        select sprint list
        """
        res = super().list(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_200_OK)

    @extend_schema(responses=unite_response_format_schema('select-sprint-detail', SprintRetrieveSerializer))
    def retrieve(self, request, *args, **kwargs):
        """
        select sprint detail
        """
        res = super().retrieve(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_200_OK)

    @extend_schema(
        responses=unite_response_format_schema('update-sprint-detail', SprintCreateUpdateSerializer))
    def update(self, request, *args, **kwargs):
        """
        update sprint detail
        """
        res = super().update(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000)

    @extend_schema(
        responses=unite_response_format_schema('partial-update-sprint-detail', SprintCreateUpdateSerializer))
    def partial_update(self, request, *args, **kwargs):
        """
        partial update sprint detail
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        delete sprint
        """
        return super().destroy(request, *args, **kwargs)
