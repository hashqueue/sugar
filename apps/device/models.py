from django.db import models
from utils.django_utils.base_model import BaseModel


class Device(BaseModel):
    """
    设备
    """
    DEVICE_TYPE_CHOICES = [(0, '阿里云ECS'), (1, '腾讯云ECS'), (2, 'Raspberry Pi(树莓派)')]
    DEVICE_STATUS_CHOICES = [(0, '离线'), (1, '在线')]
    username = models.CharField(max_length=255, verbose_name='用户名', help_text='用户名', db_index=True)
    password = models.CharField(max_length=255, verbose_name='密码(加密)', help_text='密码(加密)')
    host = models.CharField(max_length=255, verbose_name='域名或IP', help_text='域名或IP', db_index=True)
    is_deployed_agent = models.BooleanField(default=False, verbose_name='是否已部署agent', help_text='是否已部署agent')
    port = models.IntegerField(verbose_name='端口', help_text='端口')
    device_type = models.PositiveSmallIntegerField(choices=DEVICE_TYPE_CHOICES, default=0, verbose_name='设备类型',
                                                   help_text='设备类型', db_index=True)
    device_status = models.PositiveSmallIntegerField(choices=DEVICE_STATUS_CHOICES, default=0, verbose_name='设备状态',
                                                     help_text='设备状态', db_index=True)

    class Meta:
        db_table = 'device'
        verbose_name = '设备'
        verbose_name_plural = verbose_name

    def __str__(self):
        return dict(self.DEVICE_TYPE_CHOICES).get(self.device_type)
