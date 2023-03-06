from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema
from django_filters import rest_framework as filters

from utils.drf_utils.custom_json_response import JsonResponse, unite_response_format_schema
from pm.serializers.work_items import WorkItemCreateUpdateSerializer, WorkItemRetrieveSerializer
from pm.models import WorkItem, Changelog


class WorkItemFilter(filters.FilterSet):
    owner = filters.CharFilter(field_name='owner', lookup_expr='icontains', label='负责人(模糊搜索且不区分大小写)')
    name = filters.CharFilter(field_name='name', lookup_expr='icontains', label='工作项名称(模糊搜索且不区分大小写)')
    desc = filters.CharFilter(field_name='desc', lookup_expr='icontains', label='描述(模糊搜索且不区分大小写)')
    creator = filters.CharFilter(field_name='creator', lookup_expr='icontains', label='创建人(模糊搜索且不区分大小写)')
    sprint_id = filters.NumberFilter(field_name='sprint', label='所属迭代ID')

    class Meta:
        model = WorkItem
        fields = ['sprint_id', 'name', 'work_item_status', 'owner', 'work_item_type', 'priority', 'severity',
                  'bug_type', 'process_result', 'desc', 'creator']


@extend_schema(tags=['工作项管理'])
class WorkItemViewSet(ModelViewSet):
    queryset = WorkItem.objects.all().order_by('-id')
    filterset_class = WorkItemFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return WorkItemCreateUpdateSerializer
        elif self.action in ['retrieve', 'destroy', 'list']:
            return WorkItemRetrieveSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user.username, modifier=self.request.user.username)

    def perform_update(self, serializer):
        origin_work_item_obj = WorkItem.objects.get(id=self.kwargs.get('pk'))
        origin_data: dict = WorkItemCreateUpdateSerializer(instance=origin_work_item_obj).data
        serializer.save(modifier=self.request.user.username)  # 更新数据并入库
        current_data: dict = serializer.data
        ignore_columns = ['id', 'create_time', 'update_time', 'creator', 'modifier', 'sprint', 'parent',
                          'work_item_type', 'followers']
        mapping_columns_data = {'priority': dict(WorkItem.PRIORITY_CHOICES),
                                'work_item_status': dict(WorkItem.WORK_ITEM_STATUS_CHOICES),
                                'severity': dict(WorkItem.SEVERITY_CHOICES),
                                'bug_type': dict(WorkItem.BUG_TYPE_CHOICES),
                                'process_result': dict(WorkItem.PROCESS_RESULT_CHOICES)}
        columns_desc = {'name': '标题', 'owner': '负责人', 'priority': '优先级', 'work_item_status': '状态',
                        'severity': '严重程度', 'bug_type': '缺陷类型', 'process_result': '处理结果', 'desc': '描述',
                        'deadline': '截止日期', 'followers': '关注者'}
        diff_results = []
        for key, value in current_data.items():
            if key not in ignore_columns:
                if value != origin_data.get(key):
                    # 当前值与历史值不同时
                    if key in mapping_columns_data.keys():
                        diff_results.append({'key': key, 'desc': columns_desc.get(key),
                                             'origin': self.check_is_value_null(
                                                 mapping_columns_data.get(key).get(origin_data.get(key))),
                                             'current': self.check_is_value_null(
                                                 mapping_columns_data.get(key).get(value))})
                    else:
                        diff_results.append({'key': key, 'desc': columns_desc.get(key),
                                             'origin': self.check_is_value_null(origin_data.get(key)),
                                             'current': self.check_is_value_null(value)})
        Changelog.objects.create(changelog=diff_results, work_item=WorkItem.objects.get(id=self.kwargs.get('pk')),
                                 creator=self.request.user.username)

    @staticmethod
    def check_is_value_null(value):
        if value is None:
            return 'null'
        return value

    @extend_schema(responses=unite_response_format_schema('create-work-item', WorkItemCreateUpdateSerializer))
    def create(self, request, *args, **kwargs):
        """
        create work-item
        """
        res = super().create(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_201_CREATED,
                            headers=res.headers)

    def list(self, request, *args, **kwargs):
        """
        select work-item list
        """
        res = super().list(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_200_OK)

    @extend_schema(responses=unite_response_format_schema('select-work-item-detail', WorkItemRetrieveSerializer))
    def retrieve(self, request, *args, **kwargs):
        """
        select work-item detail
        """
        res = super().retrieve(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000, status=status.HTTP_200_OK)

    @extend_schema(
        responses=unite_response_format_schema('update-work-item-detail', WorkItemCreateUpdateSerializer))
    def update(self, request, *args, **kwargs):
        """
        update work-item detail
        """
        res = super().update(request, *args, **kwargs)
        return JsonResponse(data=res.data, msg='success', code=20000)

    @extend_schema(
        responses=unite_response_format_schema('partial-update-work-item-detail', WorkItemCreateUpdateSerializer))
    def partial_update(self, request, *args, **kwargs):
        """
        partial update work-item detail
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        delete work-item
        """
        return super().destroy(request, *args, **kwargs)
