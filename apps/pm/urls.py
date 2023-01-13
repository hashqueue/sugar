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

router = routers.DefaultRouter()
router.register(prefix=r'projects', viewset=ProjectViewSet, basename='project')
router.register(prefix=r'sprints', viewset=SprintViewSet, basename='sprint')
urlpatterns = [
    path('', include(router.urls)),
]
