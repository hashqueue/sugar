# -*- coding: utf-8 -*-
# @File    : custom_permissions.py
# @Software: PyCharm
# @Description:
import re
from rest_framework import permissions
from sugar.settings import WHITE_URL_LIST, API_PREFIX
from utils.drf_utils.model_utils import get_user_permissions


class RbacPermission(permissions.BasePermission):
    """
    自定义权限类
    """

    def has_permission(self, request, view):
        request_url_path = request.path
        request_method = request.method
        """演示环境禁止删除数据"""
        # if request.method == 'DELETE':
        #     return False
        """URL白名单 如果请求url在白名单, 放行"""
        for safe_url in WHITE_URL_LIST:
            if re.match(f'^{safe_url}$', request_url_path):
                return True
        """如果用户是超级用户, 则放开权限(只用作系统初始化时注册的superuser用户添加初始数据时使用)"""
        if request.user.is_superuser:
            return True
        """RBAC API权限验证"""
        # API权限验证
        user_permissions = get_user_permissions(request.user)
        for user_permission in user_permissions:
            if user_permission.get('method') == request_method and re.match(
                    f"^{(API_PREFIX + user_permission.get('url_path'))}$",
                    request_url_path):
                return True

    # def has_object_permission(self, request, view, obj):
    #     """
    #     对象级别的权限控制
    #     @param request:
    #     @param view:
    #     @param obj:
    #     @return:
    #     """
    #     pass
