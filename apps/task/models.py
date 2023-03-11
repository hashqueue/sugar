import uuid

from django.db import models

from device.models import Device
from utils.django_utils.base_model import BaseModel


class TaskResult(BaseModel):
    TASK_STATE_CHOICES = [(0, 'PENDING'), (1, 'RECEIVED'), (2, 'STARTED'), (3, 'SUCCESS'), (4, 'FAILURE'),
                          (5, 'REVOKED'), (6, 'RETRY'), (7, 'IGNORED'), (8, 'Queued')]
    TASK_TYPE_CHOICES = [(0, '采集设备性能数据'), (1, '向设备部署性能采集agent程序')]
    task_uuid = models.UUIDField(unique=True, primary_key=True, default=uuid.uuid4, editable=False, db_index=True,
                                 verbose_name='任务ID', help_text='任务ID')
    task_status = models.PositiveSmallIntegerField(choices=TASK_STATE_CHOICES, default=0, verbose_name='任务状态',
                                                   help_text='任务状态', db_index=True)
    task_type = models.PositiveSmallIntegerField(choices=TASK_TYPE_CHOICES, default=0, verbose_name='任务类型',
                                                 help_text='任务类型', db_index=True)
    log = models.TextField(blank=True, default='', verbose_name='任务执行的log', help_text='任务执行的log')
    result = models.JSONField(null=True, default=None, verbose_name='任务执行结果', help_text='任务执行结果')
    traceback = models.TextField(blank=True, default='', verbose_name='Task Traceback',
                                 help_text='任务执行异常时的堆栈信息')
    metadata = models.JSONField(null=True, default=None, verbose_name='任务元数据信息',
                                help_text='任务元数据信息(e.g. arguments, keyword arguments, etc.)')
    device = models.ForeignKey(Device, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="所属设备",
                               help_text='所属设备')

    class Meta:
        db_table = 'task_result'
        verbose_name = '任务执行结果'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.task_uuid
