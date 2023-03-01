from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from django_filters import rest_framework as filters

from system.serializers.users import UserThinRetrieveSerializer, GetAllUserSerializer
from utils.drf_utils.custom_json_response import JsonResponse, unite_response_format_schema
from pm.serializers.projects import ProjectCreateUpdateSerializer, ProjectRetrieveSerializer
from pm.models import Project
from system.models import User


class ProjectFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains', label='项目名称(模糊搜索且不区分大小写)')
    owner = filters.CharFilter(field_name='owner', lookup_expr='icontains', label='负责人(模糊搜索且不区分大小写)')

    class Meta:
        model = Project
        fields = ['name', 'project_status', 'owner']


@extend_schema(tags=['项目管理'])
class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all().order_by('-id')
    filterset_class = ProjectFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProjectCreateUpdateSerializer
        elif self.action in ['retrieve', 'destroy', 'list']:
            return ProjectRetrieveSerializer

    @staticmethod
    def init_project_members(request):
        # 新建项目时初始化项目成员，默认添加 项目负责人 和 发起当前请求的用户
        init_members = set()
        owner_id = User.objects.filter(username=request.data.get('owner', '')).first().id
        init_members.add(owner_id)
        init_members.add(request.user.id)
        return list(init_members)

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user.username, modifier=self.request.user.username,
                        members=self.init_project_members(self.request))

    def perform_update(self, serializer):
        # 更新项目时判断是否更新了 项目负责人
        if self.request.data.get('owner', False):
            project_id = self.kwargs.get('pk')
            project_obj = Project.objects.filter(id=project_id).first()
            if self.request.data.get('owner') != project_obj.owner:
                members = set()
                exists_members_qs = project_obj.members.values('id')
                # 查询已有的成员
                for exists_member in exists_members_qs:
                    members.add(exists_member.get('id'))
                # 在已有的成员里添加 新的 初始化成员
                for init_member in self.init_project_members(self.request):
                    members.add(init_member)
                serializer.save(modifier=self.request.user.username, members=list(members))
        serializer.save(modifier=self.request.user.username)

    @extend_schema(responses=unite_response_format_schema('create-project', ProjectCreateUpdateSerializer))
    def create(self, request, *args, **kwargs):
        """
        create project

        @`project_status` = [(0, '未开始'), (1, '进行中'), (2, '已完成')]
        """
        res = super().create(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_201_CREATED,
                            headers=res.headers)

    def list(self, request, *args, **kwargs):
        """
        select project list
        """
        # 只返回 当前请求的用户在项目的成员中 的数据
        queryset = self.filter_queryset(
            Project.objects.filter(members__username__contains=self.request.user.username).all().order_by('-id'))
        page = self.paginate_queryset(queryset)
        if page is not None:
            # 分页
            serializer = self.get_serializer(page, many=True)
            paginated_data = self.get_paginated_response(serializer.data).data
            return JsonResponse(data=paginated_data, msg='success', code=20000, status=status.HTTP_200_OK)
        serializer = self.get_serializer(queryset, many=True)
        return JsonResponse(data=serializer.data, msg='success', code=20000, status=status.HTTP_200_OK)

    @extend_schema(responses=unite_response_format_schema('select-project-detail', ProjectRetrieveSerializer))
    def retrieve(self, request, *args, **kwargs):
        """
        select project detail
        """
        res = super().retrieve(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_200_OK)

    @extend_schema(
        responses=unite_response_format_schema('update-project-detail', ProjectCreateUpdateSerializer))
    def update(self, request, *args, **kwargs):
        """
        update project detail
        """
        res = super().update(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000)

    @extend_schema(
        responses=unite_response_format_schema('partial-update-project-detail',
                                               ProjectCreateUpdateSerializer))
    def partial_update(self, request, *args, **kwargs):
        """
        partial update project detail
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        delete project
        """
        return super().destroy(request, *args, **kwargs)

    @extend_schema(responses=unite_response_format_schema('get-project-members', GetAllUserSerializer))
    @action(methods=['get'], detail=True, url_path='members')
    def get_user_statistics(self, request, pk=None, version=None):
        """
        获取当前项目下的所有成员
        """
        serializer = UserThinRetrieveSerializer(
            User.objects.filter(id__in=Project.objects.filter(id=pk).values('members')).all(), many=True,
            context={'request': request})
        return JsonResponse(data={'results': serializer.data, 'count': len(serializer.data)}, msg='success', code=20000)
