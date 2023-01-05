# -*- coding: utf-8 -*-
# @File    : base_model.py
# @Software: PyCharm
# @Description:
from django.db import models


class BaseModel(models.Model):
    """
    数据库表公共字段
    """
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')

    class Meta:
        # 设置当前模型类为抽象类，用于其他模型类来继承，数据库迁移时不会创建当前模型类的表
        abstract = True
        verbose_name = '公共字段表'
