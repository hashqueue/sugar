from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from django_filters import rest_framework as filters

from utils.drf_utils.custom_json_response import JsonResponse, unite_response_format_schema
from system.serializers.organizations import OrganizationCreateUpdateSerializer, OrganizationRetrieveSerializer, \
    OrganizationTreeListSerializer, OrganizationBaseRetrieveSerializer
from system.models import Organization
from utils.drf_utils.model_utils import generate_object_tree_data


class OrganizationNameFilter(filters.FilterSet):
    """
    自定义过滤器类，实现对组织架构名称进行模糊搜索(不区分大小写)
    """
    name = filters.CharFilter(field_name='name', lookup_expr='icontains', label='组织架构名称(模糊搜索且不区分大小写)')

    class Meta:
        model = Organization
        fields = ['name']


@extend_schema(tags=['组织架构管理'])
class OrganizationViewSet(ModelViewSet):
    queryset = Organization.objects.all().order_by('-id')
    filterset_class = OrganizationNameFilter

    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'partial_update' or self.action == 'create':
            return OrganizationCreateUpdateSerializer
        elif self.action == 'retrieve' or self.action == 'destroy':
            return OrganizationRetrieveSerializer
        elif self.action == 'list':
            return OrganizationBaseRetrieveSerializer
        elif self.action == 'get_organization_tree_list':
            return OrganizationTreeListSerializer

    @extend_schema(responses=unite_response_format_schema('create-organization', OrganizationCreateUpdateSerializer))
    def create(self, request, *args, **kwargs):
        """
        create organization
        """
        res = super().create(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_201_CREATED,
                            headers=res.headers)

    def list(self, request, *args, **kwargs):
        """
        select organization list
        """
        res = super().list(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_200_OK)

    @extend_schema(responses=unite_response_format_schema('select-organization-detail', OrganizationRetrieveSerializer))
    def retrieve(self, request, *args, **kwargs):
        """
        select organization detail
        """
        res = super().retrieve(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_200_OK)

    @extend_schema(
        responses=unite_response_format_schema('update-organization-detail', OrganizationCreateUpdateSerializer))
    def update(self, request, *args, **kwargs):
        """
        update organization detail
        """
        res = super().update(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000)

    @extend_schema(
        responses=unite_response_format_schema('partial-update-organization-detail',
                                               OrganizationCreateUpdateSerializer))
    def partial_update(self, request, *args, **kwargs):
        """
        partial update organization detail
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        delete organization
        """
        return super().destroy(request, *args, **kwargs)

    @extend_schema(responses=unite_response_format_schema('get-organization-tree-list', OrganizationTreeListSerializer))
    @action(methods=['get'], detail=False, url_path='tree')
    def get_organization_tree_list(self, request, *args, **kwargs):
        """
        select organization tree list
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
