# -*- coding: utf-8 -*-
# @Time    : 2021/3/22 下午1:49
# @Author  : anonymous
# @File    : urls.py
# @Software: PyCharm
# @Description:
from django.urls import path, include
from rest_framework import routers

from pm.views.project import ProjectViewSet
from pm.views.sprint import SprintViewSet
from pm.views.work_item import WorkItemViewSet

router = routers.DefaultRouter()
router.register(prefix=r'projects', viewset=ProjectViewSet, basename='project')
router.register(prefix=r'sprints', viewset=SprintViewSet, basename='sprint')
router.register(prefix=r'work-items', viewset=WorkItemViewSet, basename='work-item')
urlpatterns = [
    path('', include(router.urls)),
]
