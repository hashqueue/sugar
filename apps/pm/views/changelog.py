from rest_framework import status
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from drf_spectacular.utils import extend_schema
from django_filters import rest_framework as filters

from utils.drf_utils.custom_json_response import JsonResponse, unite_response_format_schema
from pm.serializers.changelogs import ChangelogRetrieveSerializer
from pm.models import Changelog


class ChangelogFilter(filters.FilterSet):
    work_item_id = filters.NumberFilter(field_name='work_item', label='所属工作项ID')

    class Meta:
        model = Changelog
        fields = ['work_item_id']


@extend_schema(tags=['工作项变更记录管理'])
class ChangelogViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    queryset = Changelog.objects.all().order_by('-id')
    filterset_class = ChangelogFilter
    serializer_class = ChangelogRetrieveSerializer

    def list(self, request, *args, **kwargs):
        """
        select changelog list
        """
        res = super().list(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_200_OK)

    @extend_schema(responses=unite_response_format_schema('select-changelog-detail', ChangelogRetrieveSerializer))
    def retrieve(self, request, *args, **kwargs):
        """
        select changelog detail
        """
        res = super().retrieve(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_200_OK)
