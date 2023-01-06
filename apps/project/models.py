from django.db import models
from utils.django_utils.base_model import BaseModel
from system.models import User


class Project(BaseModel):
    """
    项目
    """
    name = models.CharField(max_length=64, verbose_name="项目名称", help_text='项目名称')
    users = models.ManyToManyField(User, blank=True, verbose_name="项目成员", help_text='项目成员')

    class Meta:
        db_table = 'project'
        verbose_name = '项目'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Sprint(BaseModel):
    """
    迭代
    """
    name = models.CharField(max_length=64, verbose_name="迭代名称", help_text='迭代名称')
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="所属项目",
                                help_text='所属项目')

    class Meta:
        db_table = 'project_sprint'
        verbose_name = '迭代'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Feature(BaseModel):
    """
    需求
    """
    name = models.CharField(max_length=64, verbose_name="需求名称", help_text='需求名称')
    sprint = models.ForeignKey(Sprint, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="所属迭代",
                               help_text='所属迭代')

    class Meta:
        db_table = 'project_feature'
        verbose_name = '需求'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Task(BaseModel):
    """
    任务
    """
    name = models.CharField(max_length=64, verbose_name="任务名称", help_text='任务名称')
    sprint = models.ForeignKey(Sprint, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="所属迭代",
                               help_text='所属迭代')

    class Meta:
        db_table = 'project_Task'
        verbose_name = '任务'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Bug(BaseModel):
    """
    Bug
    """
    name = models.CharField(max_length=64, verbose_name="Bug名称", help_text='Bug名称')
    sprint = models.ForeignKey(Sprint, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="所属迭代",
                               help_text='所属迭代')

    class Meta:
        db_table = 'project_bug'
        verbose_name = 'Bug'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
