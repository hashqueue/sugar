from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

from pm.models import Changelog
from system.models import User
from utils.drf_utils.base_model_serializer import BaseModelSerializer


class ChangelogRetrieveSerializer(BaseModelSerializer):
    creator_name = serializers.SerializerMethodField(help_text='创建人姓名')

    class Meta:
        model = Changelog
        fields = '__all__'

    @extend_schema_field(OpenApiTypes.STR)
    def get_creator_name(self, obj: Changelog):
        return User.objects.filter(username=obj.creator).first().name
