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

    class Meta:
        model = Project
        fields = '__all__'
