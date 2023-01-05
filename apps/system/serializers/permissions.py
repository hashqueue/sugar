from rest_framework import serializers
from system.models import Permission
from utils.drf_utils.base_model_serializer import BaseModelSerializer
from utils.drf_utils.model_utils import get_obj_child_ids


class PermissionCreateUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'
        read_only_fields = ('id', 'create_time', 'update_time')

    def update(self, instance, validated_data):
        parent = validated_data.get('parent', False)
        is_menu = validated_data.get('is_menu')
        if parent:
            if is_menu and Permission.objects.get(id=parent.id).is_menu is False:
                raise serializers.ValidationError('菜单父权限必须为菜单权限.')
            if parent.id == instance.id:
                raise serializers.ValidationError('父权限不能为其本身.', code=40000)
            ids = set()
            get_obj_child_ids(instance.id, Permission, ids)
            # print(ids)
            if parent.id in ids:
                raise serializers.ValidationError('父权限不能为其子权限.', code=40000)
        return super().update(instance, validated_data)

    def validate(self, attrs):
        icon: str = attrs.get('icon')
        path: str = attrs.get('path')
        url_path: str = attrs.get('url_path')
        method: str = attrs.get('method')
        if attrs.get('is_menu'):
            if icon and path:
                pass
            else:
                raise serializers.ValidationError('新增或修改菜单权限时, 图标和路由path不能为空.')
            if method or url_path:
                raise serializers.ValidationError('新增或修改菜单权限时, 请求方法和请求路径必须为空.')
        else:
            if method and url_path:
                if not all([url_path.startswith('/'), url_path.endswith('/')]):
                    raise serializers.ValidationError('请求路径必须以`/`开头及结尾.')
            else:
                raise serializers.ValidationError('新增或修改接口权限时, 请求方法和请求路径不能为空.')
            if icon or path:
                raise serializers.ValidationError('新增或修改接口权限时, 图标和路由path必须为空.')
        return attrs

    def create(self, validated_data):
        parent = validated_data.get('parent', False)
        if validated_data.get('is_menu', False) and parent and Permission.objects.get(id=parent.id).is_menu is False:
            raise serializers.ValidationError('菜单父权限必须为菜单权限.')
        return super().create(validated_data)


class PermissionBaseRetrieveSerializer(BaseModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class PermissionTreeSerializer(PermissionBaseRetrieveSerializer):
    children = PermissionBaseRetrieveSerializer(many=True, read_only=True)


class GetPermissionsTreeWithRoleIdsSerializer(serializers.ModelSerializer):
    menu_permissions = PermissionBaseRetrieveSerializer(many=True, read_only=True)
    api_permissions = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = Permission
        fields = ('menu_permissions', 'api_permissions')
        read_only_fields = ('menu_permissions', 'api_permissions')


class PermissionRetrieveSerializer(PermissionBaseRetrieveSerializer):
    parent = PermissionBaseRetrieveSerializer()

    class Meta:
        model = Permission
        fields = '__all__'
