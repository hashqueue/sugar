from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema

from utils.drf_utils.custom_json_response import JsonResponse, unite_response_format_schema
from project.serializers.projects import ProjectCreateUpdateSerializer, ProjectRetrieveSerializer
from project.models import Project


@extend_schema(tags=['项目管理'])
class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all().order_by('-id')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProjectCreateUpdateSerializer
        elif self.action in ['retrieve', 'destroy', 'list']:
            return ProjectRetrieveSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user.username, modifier=self.request.user.username)

    def perform_update(self, serializer):
        serializer.save(modifier=self.request.user.username)

    @extend_schema(responses=unite_response_format_schema('create-project', ProjectCreateUpdateSerializer))
    def create(self, request, *args, **kwargs):
        """
        create project

        `status` [(0, '未开始'), (1, '进行中'), (2, '已完成')]
        """
        res = super().create(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_201_CREATED,
                            headers=res.headers)

    def list(self, request, *args, **kwargs):
        """
        select project list

        `status` [(0, '未开始'), (1, '进行中'), (2, '已完成')]
        """
        res = super().list(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_200_OK)

    @extend_schema(responses=unite_response_format_schema('select-project-detail', ProjectRetrieveSerializer))
    def retrieve(self, request, *args, **kwargs):
        """
        select project detail

        `status` [(0, '未开始'), (1, '进行中'), (2, '已完成')]
        """
        res = super().retrieve(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_200_OK)

    @extend_schema(
        responses=unite_response_format_schema('update-project-detail', ProjectCreateUpdateSerializer))
    def update(self, request, *args, **kwargs):
        """
        update project detail

        `status` [(0, '未开始'), (1, '进行中'), (2, '已完成')]
        """
        res = super().update(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000)

    @extend_schema(
        responses=unite_response_format_schema('partial-update-project-detail',
                                               ProjectCreateUpdateSerializer))
    def partial_update(self, request, *args, **kwargs):
        """
        partial update project detail

        `status` [(0, '未开始'), (1, '进行中'), (2, '已完成')]
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        delete project

        `status` [(0, '未开始'), (1, '进行中'), (2, '已完成')]
        """
        return super().destroy(request, *args, **kwargs)
