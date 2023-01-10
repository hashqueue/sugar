from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

from system.models import User
from project.models import Project
from system.serializers.users import UserThinRetrieveSerializer
from utils.drf_utils.base_model_serializer import BaseModelSerializer


class ProjectCreateUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ('id', 'create_time', 'update_time', 'creator', 'modifier')


class ProjectRetrieveSerializer(BaseModelSerializer):
    members = UserThinRetrieveSerializer(many=True, read_only=True)
    owner_name = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = '__all__'

    @extend_schema_field(OpenApiTypes.STR)
    def get_owner_name(self, obj):
        return User.objects.get(username=obj.owner).name
