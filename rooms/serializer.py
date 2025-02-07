from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Room, Membership


class RoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"

class MembershipSerializer(ModelSerializer):
    class Meta:
        model = Membership
        fields = "__all__"