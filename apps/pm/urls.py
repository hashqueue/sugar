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
from pm.views.user_file import UserFileViewSet
from pm.views.comment import CommentViewSet

router = routers.DefaultRouter()
router.register(prefix=r'projects', viewset=ProjectViewSet, basename='project')
router.register(prefix=r'sprints', viewset=SprintViewSet, basename='sprint')
router.register(prefix=r'work-items', viewset=WorkItemViewSet, basename='work-item')
router.register(prefix=r'files', viewset=UserFileViewSet, basename='user-file')
router.register(prefix=r'comments', viewset=CommentViewSet, basename='comment')
urlpatterns = [
    path('', include(router.urls)),
]
