# -*- coding: utf-8 -*-
# @File    : custom_user_authentication_backend.py
# @Software: PyCharm
# @Description:
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.contrib.auth import get_user_model

User = get_user_model()


class MyCustomUserAuthBackend(ModelBackend):
    """
    自定义用户认证后端，可以使用username+password或email+password来进行认证登录
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
