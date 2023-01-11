# -*- coding: utf-8 -*-
# @File    : users.py
# @Software: PyCharm
# @Description:
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from system.models import User
from system.serializers.organizations import OrganizationBaseRetrieveSerializer
from system.serializers.roles import RoleBaseRetrieveSerializer
from sugar.settings import DEFAULT_USER_PASSWORD


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    用户注册序列化器
    """
    password_confirm = serializers.CharField(min_length=8,
                                             max_length=128,
                                             label='确认密码',
                                             help_text='确认密码',
                                             write_only=True,
                                             required=True,
                                             allow_blank=False,
                                             error_messages={
                                                 'min_length': '密码长度不能小于8',
                                                 'max_length': '密码长度不能大于128', })

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'password_confirm')
        extra_kwargs = {
            'username': {
                'label': '用户名',
                'help_text': '用户名',
                'min_length': 1,
                'max_length': 150,
                'error_messages': {
                    'min_length': '用户名长度不能小于1',
                    'max_length': '用户名长度不能大于150',
                }
            },
            'password': {
                'label': '密码',
                'help_text': '密码',
                'write_only': True,
                'required': True,
                'min_length': 8,
                'max_length': 128,
                'error_messages': {
                    'min_length': '密码长度不能小于8',
                    'max_length': '密码长度不能大于128',
                }
            },
            'email': {
                'label': '邮箱',
                'help_text': '邮箱',
                'required': True,
                # 添加邮箱重复校验
                'validators': [UniqueValidator(queryset=User.objects.all(), message='此邮箱已被使用')],
            },
        }

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        if password != password_confirm:
            raise serializers.ValidationError('两次输入密码不一致')
        return attrs

    def create(self, validated_data):
        # 移除数据库模型类中不存在的字段password_confirm
        validated_data.pop('password_confirm')
        # 创建用户实例
        user_instance = User.objects.create_user(**validated_data)
        return user_instance


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        """
        重写validate方法, 添加user_id字段
        :param attrs:
        :return:
        """
        data = super().validate(attrs)
        data['user_id'] = self.user.id
        return {"code": 20000, "message": "登录成功", "data": data}


class UserCreateUpdateSerializer(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True, help_text='加入时间')

    class Meta:
        model = User
        exclude = ('password', 'avatar', 'first_name', 'last_name',
                   'is_staff', 'groups', 'user_permissions', 'last_login')
        read_only_fields = ('id', 'date_joined')

    def create(self, validated_data):
        user = super().create(validated_data)
        # 添加默认密码
        user.set_password(DEFAULT_USER_PASSWORD)
        user.save()
        return user


class UserListDestroySerializer(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True, help_text='加入时间')
    department = serializers.SlugRelatedField(slug_field='name', many=False, read_only=True)
    roles = serializers.SlugRelatedField(slug_field='name', many=True, read_only=True)

    class Meta:
        model = User
        exclude = ('password', 'groups', 'user_permissions', 'first_name', 'last_name', 'last_login')


class UserThinRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'avatar', 'name', 'position')


class GetAllUserSerializer(serializers.ModelSerializer):
    results = UserThinRetrieveSerializer(many=True, read_only=True)
    count = serializers.IntegerField(help_text='用户总数量')

    class Meta:
        model = User
        fields = ('results', 'count')


class UserRetrieveSerializer(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True, help_text='加入时间')
    department = OrganizationBaseRetrieveSerializer(many=False, read_only=True)
    roles = RoleBaseRetrieveSerializer(many=True, read_only=True)

    class Meta:
        model = User
        exclude = ('password', 'groups', 'user_permissions', 'first_name', 'last_name', 'last_login')


class UserResetPasswordSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(min_length=8,
                                             max_length=128,
                                             label='确认密码',
                                             help_text='确认密码',
                                             write_only=True,
                                             required=True,
                                             allow_blank=False,
                                             error_messages={
                                                 'min_length': '密码长度不能小于8',
                                                 'max_length': '密码长度不能大于128', })

    class Meta:
        model = User
        fields = ('username', 'password', 'password_confirm')
        read_only_fields = ('username',)
        extra_kwargs = {
            'password': {
                'label': '密码',
                'help_text': '密码',
                'write_only': True,
                'required': True,
                'min_length': 8,
                'max_length': 128,
                'error_messages': {
                    'min_length': '密码长度不能小于8',
                    'max_length': '密码长度不能大于128',
                }
            }
        }

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        if password != password_confirm:
            raise serializers.ValidationError('两次输入密码不一致')
        return attrs
