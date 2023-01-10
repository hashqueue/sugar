import logging
from drf_spectacular.utils import extend_schema
from rest_framework import status, serializers
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from django_filters import rest_framework as filters

from utils.drf_utils.custom_json_response import JsonResponse, unite_response_format_schema
from system.serializers.permissions import PermissionCreateUpdateSerializer, PermissionRetrieveSerializer, \
    GetPermissionsTreeWithRoleIdsSerializer, PermissionTreeSerializer, PermissionBaseRetrieveSerializer
from system.models import Permission, Role
from utils.drf_utils.model_utils import generate_object_tree_data

logger = logging.getLogger('my_debug_logger')


class PermissionFilter(filters.FilterSet):
    title = filters.CharFilter(field_name='title', lookup_expr='icontains', label='权限名称(模糊搜索且不区分大小写)')

    class Meta:
        model = Permission
        fields = ['title']


@extend_schema(tags=['权限管理'])
class PermissionViewSet(ModelViewSet):
    queryset = Permission.objects.all().order_by('-id')
    filterset_class = PermissionFilter

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update', 'create']:
            return PermissionCreateUpdateSerializer
        elif self.action in ['retrieve', 'destroy']:
            return PermissionRetrieveSerializer
        elif self.action == 'list':
            return PermissionBaseRetrieveSerializer
        elif self.action == 'get_permissions_whit_roles':
            return GetPermissionsTreeWithRoleIdsSerializer
        elif self.action == 'get_permission_tree_list':
            return PermissionTreeSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user.username, modifier=self.request.user.username)

    def perform_update(self, serializer):
        serializer.save(modifier=self.request.user.username)

    @extend_schema(responses=unite_response_format_schema('create-permission', PermissionCreateUpdateSerializer))
    def create(self, request, *args, **kwargs):
        """
        create permission
        """
        res = super().create(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_201_CREATED,
                            headers=res.headers)

    def list(self, request, *args, **kwargs):
        """
        select permission list
        """
        res = super().list(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_200_OK)

    @extend_schema(responses=unite_response_format_schema('select-permission-detail', PermissionRetrieveSerializer))
    def retrieve(self, request, *args, **kwargs):
        """
        select permission detail
        """
        res = super().retrieve(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_200_OK)

    @extend_schema(
        responses=unite_response_format_schema('update-permission-detail', PermissionCreateUpdateSerializer))
    def update(self, request, *args, **kwargs):
        """
        update permission detail
        """
        res = super().update(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000)

    @extend_schema(
        responses=unite_response_format_schema('partial-update-permission-detail',
                                               PermissionCreateUpdateSerializer))
    def partial_update(self, request, *args, **kwargs):
        """
        partial update permission detail
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        delete permission
        """
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        responses=unite_response_format_schema('get-user-permissions', GetPermissionsTreeWithRoleIdsSerializer))
    @action(methods=['get'], detail=False, url_path='get-user-permissions')
    def get_current_user_permissions(self, request, pk=None, version=None):
        """
        获取当前登录用户的权限
        """
        roles_permissions = []
        role_ids = [role.id for role in self.request.user.roles.all()]
        for role_id in role_ids:
            role_objs = Role.objects.filter(id=role_id).all()
            if len(role_objs) == 0:
                raise serializers.ValidationError(f'id为{role_id}的角色不存在.')
            roles_permissions.extend(role_objs[0].permissions.all())
        roles_permissions = list(set(roles_permissions))
        # 获取权限list
        permissions_serializer = PermissionBaseRetrieveSerializer(roles_permissions, many=True)
        api_permissions = []
        menu_permissions = []
        for item in permissions_serializer.data:
            if item.get('is_menu'):
                menu_permissions.append(item)
            else:
                api_permissions.append(item.get('title'))
        return JsonResponse(data={'menu_permissions': menu_permissions, 'api_permissions': api_permissions},
                            msg='success', code=20000)

    @extend_schema(responses=unite_response_format_schema('get-permission-tree-list', PermissionTreeSerializer))
    @action(methods=['get'], detail=False, url_path='tree')
    def get_permission_tree_list(self, request, *args, **kwargs):
        """
        select permission tree list
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        results = generate_object_tree_data(serializer.data)
        if results:
            return JsonResponse(data=results, msg='success', code=20000)
        else:
            # 生成tree型数据报错时，按照非tree格式、drf原始分页格式来返回数据
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                res = self.get_paginated_response(serializer.data)
                return JsonResponse(data=res.data, msg='success', code=20000)
            return JsonResponse(data=serializer.data, msg='success', code=20000)
