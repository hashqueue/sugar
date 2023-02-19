from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema
from django_filters import rest_framework as filters

from utils.drf_utils.custom_json_response import JsonResponse, unite_response_format_schema
from pm.serializers.comments import CommentCreateUpdateSerializer, CommentRetrieveSerializer
from pm.models import Comment


class CommentFilter(filters.FilterSet):
    work_item_id = filters.NumberFilter(field_name='work_item', label='所属工作项ID')

    class Meta:
        model = Comment
        fields = ['work_item_id']


@extend_schema(tags=['评论管理'])
class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all().order_by('-id')
    filterset_class = CommentFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CommentCreateUpdateSerializer
        elif self.action in ['retrieve', 'destroy', 'list']:
            return CommentRetrieveSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user.username, modifier=self.request.user.username)

    def perform_update(self, serializer):
        serializer.save(modifier=self.request.user.username)

    @extend_schema(responses=unite_response_format_schema('create-comment', CommentCreateUpdateSerializer))
    def create(self, request, *args, **kwargs):
        """
        create comment
        """
        res = super().create(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_201_CREATED,
                            headers=res.headers)

    def list(self, request, *args, **kwargs):
        """
        select comment list
        """
        res = super().list(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_200_OK)

    @extend_schema(responses=unite_response_format_schema('select-comment-detail', CommentRetrieveSerializer))
    def retrieve(self, request, *args, **kwargs):
        """
        select comment detail
        """
        res = super().retrieve(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_200_OK)

    @extend_schema(
        responses=unite_response_format_schema('update-comment-detail', CommentCreateUpdateSerializer))
    def update(self, request, *args, **kwargs):
        """
        update comment detail
        """
        res = super().update(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000)

    @extend_schema(
        responses=unite_response_format_schema('partial-update-comment-detail', CommentCreateUpdateSerializer))
    def partial_update(self, request, *args, **kwargs):
        """
        partial update comment detail
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        delete comment
        """
        return super().destroy(request, *args, **kwargs)
