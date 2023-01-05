from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.viewsets import ModelViewSet

from utils.drf_utils.custom_json_response import JsonResponse, unite_response_format_schema
from system.serializers.roles import RoleCreateUpdateSerializer, RoleRetrieveSerializer
from system.models import Role


@extend_schema(tags=['角色管理'])
class RoleViewSet(ModelViewSet):
    queryset = Role.objects.all().order_by('-id')

    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'partial_update' or self.action == 'create':
            return RoleCreateUpdateSerializer
        elif self.action == 'retrieve' or self.action == 'destroy' or self.action == 'list':
            return RoleRetrieveSerializer

    @extend_schema(responses=unite_response_format_schema('create-role', RoleCreateUpdateSerializer))
    def create(self, request, *args, **kwargs):
        """
        create role
        """
        res = super().create(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_201_CREATED,
                            headers=res.headers)

    def list(self, request, *args, **kwargs):
        """
        select role list
        """
        res = super().list(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_200_OK)

    @extend_schema(responses=unite_response_format_schema('select-role-detail', RoleRetrieveSerializer))
    def retrieve(self, request, *args, **kwargs):
        """
        select role detail
        """
        res = super().retrieve(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_200_OK)

    @extend_schema(
        responses=unite_response_format_schema('update-role-detail', RoleCreateUpdateSerializer))
    def update(self, request, *args, **kwargs):
        """
        update role detail
        """
        res = super().update(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000)

    @extend_schema(
        responses=unite_response_format_schema('partial-update-role-detail',
                                               RoleCreateUpdateSerializer))
    def partial_update(self, request, *args, **kwargs):
        """
        partial update role detail
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        delete role
        """
        return super().destroy(request, *args, **kwargs)
