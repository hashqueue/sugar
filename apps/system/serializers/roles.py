from system.models import Role
from system.serializers.permissions import PermissionBaseRetrieveSerializer
from utils.drf_utils.base_model_serializer import BaseModelSerializer


class RoleCreateUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'
        read_only_fields = ('id', 'create_time', 'update_time')


class RoleBaseRetrieveSerializer(BaseModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class RoleRetrieveSerializer(BaseModelSerializer):
    permissions = PermissionBaseRetrieveSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = '__all__'
