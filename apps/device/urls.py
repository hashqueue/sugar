# -*- coding: utf-8 -*-
# @Time    : 2021/3/22 下午1:49
# @Author  : anonymous
# @File    : urls.py
# @Software: PyCharm
# @Description:
from django.urls import path, include
from rest_framework import routers

from device.views.device import DeviceViewSet

router = routers.DefaultRouter()
router.register(prefix=r'devices', viewset=DeviceViewSet, basename='device')
urlpatterns = [
    path('', include(router.urls)),
]
