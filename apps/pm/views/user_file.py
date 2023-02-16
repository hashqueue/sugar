from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema
from django_filters import rest_framework as filters

from utils.drf_utils.custom_json_response import JsonResponse, unite_response_format_schema
from pm.serializers.user_files import UserFileCreateUpdateSerializer, UserFileRetrieveSerializer
from pm.models import UserFile


class UserFileFilter(filters.FilterSet):
    work_item_id = filters.NumberFilter(field_name='work_item', label='所属工作项ID')

    class Meta:
        model = UserFile
        fields = ['work_item_id']


@extend_schema(tags=['用户文件管理'])
class UserFileViewSet(ModelViewSet):
    parser_classes = [MultiPartParser]
    queryset = UserFile.objects.all().order_by('-id')
    filterset_class = UserFileFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return UserFileCreateUpdateSerializer
        elif self.action in ['retrieve', 'destroy', 'list']:
            return UserFileRetrieveSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user.username, modifier=self.request.user.username)

    def perform_update(self, serializer):
        serializer.save(modifier=self.request.user.username)

    @extend_schema(responses=unite_response_format_schema('create-user-file', UserFileCreateUpdateSerializer))
    def create(self, request, *args, **kwargs):
        """
        create user-file
        """
        res = super().create(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_201_CREATED,
                            headers=res.headers)

    def list(self, request, *args, **kwargs):
        """
        select user-file list
        """
        res = super().list(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_200_OK)

    @extend_schema(responses=unite_response_format_schema('select-user-file-detail', UserFileRetrieveSerializer))
    def retrieve(self, request, *args, **kwargs):
        """
        select user-file detail
        """
        res = super().retrieve(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_200_OK)

    @extend_schema(
        responses=unite_response_format_schema('update-user-file-detail', UserFileCreateUpdateSerializer))
    def update(self, request, *args, **kwargs):
        """
        update user-file detail
        """
        res = super().update(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000)

    @extend_schema(
        responses=unite_response_format_schema('partial-update-user-file-detail', UserFileCreateUpdateSerializer))
    def partial_update(self, request, *args, **kwargs):
        """
        partial update user-file detail
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        delete user-file
        """
        return super().destroy(request, *args, **kwargs)
