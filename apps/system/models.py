import random

from django.db import models
from django.contrib.auth.models import AbstractUser
from utils.django_utils.base_model import BaseModel


class Permission(BaseModel):
    """
    权限
    """
    method_choices = (
        ('POST', '增'),
        ('DELETE', '删'),
        ('PUT', '改'),
        ('PATCH', '局部改'),
        ('GET', '查')
    )
    title = models.CharField(max_length=64, unique=True, verbose_name="权限名称", help_text='权限名称')
    parent = models.ForeignKey(to='self', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="父权限",
                               help_text='父权限')
    is_menu = models.BooleanField(verbose_name='是否为菜单(true为菜单,false为接口)',
                                  help_text='是否为菜单(true为菜单,false为接口)')
    method = models.CharField(max_length=8, blank=True, default='', choices=method_choices, verbose_name='请求方法',
                              help_text='请求方法')
    url_path = models.CharField(max_length=256, blank=True, default='', verbose_name='请求路径', help_text='请求路径')
    icon = models.CharField(max_length=64, blank=True, default='', verbose_name="图标", help_text='图标')
    component = models.CharField(max_length=256, blank=True, default='', verbose_name='组件路径',
                                 help_text='组件路径')
    path = models.CharField(max_length=256, blank=True, default='', verbose_name='路由path',
                            help_text='路由path')
    redirect = models.CharField(max_length=256, blank=True, default='', verbose_name='路由重定向path',
                                help_text='路由重定向path')
    is_visible = models.BooleanField(blank=True, null=True, verbose_name='是否显示(true为显示,false为隐藏)',
                                     help_text='是否显示(true为显示,false为隐藏)')

    class Meta:
        db_table = 'system_permission'
        verbose_name = '权限'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class Role(BaseModel):
    """
    角色：用于权限绑定
    """
    name = models.CharField(max_length=32, unique=True, verbose_name="角色名", help_text='角色名')
    permissions = models.ManyToManyField(Permission, blank=True, verbose_name="权限", help_text='权限')
    desc = models.CharField(max_length=64, blank=True, default='', verbose_name="描述", help_text='描述')

    class Meta:
        db_table = 'system_role'
        verbose_name = '角色'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Organization(BaseModel):
    """
    组织架构
    """
    type_choices = (("company", "公司"), ("department", "部门"))
    name = models.CharField(max_length=128, verbose_name="名称", help_text='名称')
    type = models.CharField(max_length=20, choices=type_choices, default="department", verbose_name="类型",
                            help_text='类型')
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, verbose_name="父组织架构",
                               help_text='父组织架构')

    class Meta:
        db_table = 'system_organization'
        verbose_name = "组织架构"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class User(AbstractUser):
    gender_choices = (("male", "男"), ("female", "女"))
    name = models.CharField(max_length=20, blank=True, default='', verbose_name="姓名", help_text='姓名')
    birthday = models.DateField(null=True, blank=True, verbose_name="出生日期", help_text='出生日期')
    gender = models.CharField(max_length=10, blank=True, default="male", choices=gender_choices, verbose_name="性别",
                              help_text='性别')
    mobile = models.CharField(max_length=11, blank=True, default='', verbose_name="手机号码", help_text='手机号码')
    avatar = models.ImageField(upload_to="avatars/", default=f"avatars/brave.png", max_length=100, blank=True,
                               verbose_name="头像", help_text='头像')
    department = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="部门",
                                   help_text='部门')
    position = models.CharField(max_length=64, blank=True, default='', verbose_name="职位", help_text='职位')
    roles = models.ManyToManyField(Role, blank=True, verbose_name="角色", help_text='角色')

    class Meta:
        db_table = 'system_user'
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
