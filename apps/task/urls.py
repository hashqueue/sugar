# -*- coding: utf-8 -*-
# @Time    : 2021/3/22 下午1:49
# @Author  : anonymous
# @File    : urls.py
# @Software: PyCharm
# @Description:
from django.urls import path, include
from rest_framework import routers

from task.views.task_result import TaskResultViewSet

router = routers.DefaultRouter()
router.register(prefix=r'tasks-results', viewset=TaskResultViewSet, basename='task')
urlpatterns = [
    path('', include(router.urls)),
]
