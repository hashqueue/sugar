# -*- coding: utf-8 -*-
# @File    : base_model_serializer.py
# @Software: PyCharm
# @Description:
from rest_framework import serializers


class BaseModelSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True, help_text='创建时间')
    update_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True, help_text='更新时间')
