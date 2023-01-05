from rest_framework import serializers
from system.models import Organization
from utils.drf_utils.base_model_serializer import BaseModelSerializer
from utils.drf_utils.model_utils import get_obj_child_ids


class OrganizationCreateUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'
        read_only_fields = ('id', 'create_time', 'update_time')

    def update(self, instance, validated_data):
        parent = validated_data.get('parent', False)
        if parent:
            if parent.id == instance.id:
                raise serializers.ValidationError('父部门不能为其本身.', code=40000)
            ids = set()
            get_obj_child_ids(instance.id, Organization, ids)
            # print(ids)
            if parent.id in ids:
                raise serializers.ValidationError('父部门不能为其子部门.', code=40000)
        return super().update(instance, validated_data)


class OrganizationBaseRetrieveSerializer(BaseModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'


class OrganizationTreeListSerializer(OrganizationBaseRetrieveSerializer):
    children = OrganizationBaseRetrieveSerializer(many=True, read_only=True)


class OrganizationRetrieveSerializer(OrganizationBaseRetrieveSerializer):
    parent = OrganizationBaseRetrieveSerializer()

    class Meta:
        model = Organization
        fields = '__all__'
