from rest_framework.serializers import ModelSerializer

from habbits.models import Habbit
from habbits.validators import habit_validation


class HabbitSerializer(ModelSerializer):
    class Meta:
        model = Habbit
        fields = "__all__"
        read_only_fields = ["user"]
        validators = [habit_validation]
