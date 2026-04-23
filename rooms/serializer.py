from rest_framework import serializers
from .models import Room, Membership, Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model."""

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'created_at', 'updated_at']
        read_only_fields = ['slug', 'created_at', 'updated_at']


class RoomSerializer(serializers.ModelSerializer):
    """Serializer for Room model with nested tags."""
    tags = TagSerializer(many=True, required=False)
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    creator_email = serializers.EmailField(source='creator.email', read_only=True)

    class Meta:
        model = Room
        fields = [
            'id', 'name', 'description', 'creator', 'creator_name', 'creator_email',
            'is_public', 'created_at', 'updated_at', 'tags', 'room_profile'
        ]
        read_only_fields = ['creator', 'created_at', 'updated_at']

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        room = super().create(validated_data)
        for tag_data in tags_data:
            tag, _ = Tag.objects.get_or_create(**tag_data)
            room.tags.add(tag)
        return room

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        room = super().update(instance, validated_data)
        if tags_data is not None:
            room.tags.clear()
            for tag_data in tags_data:
                tag, _ = Tag.objects.get_or_create(**tag_data)
                room.tags.add(tag)
        return room


class MembershipSerializer(serializers.ModelSerializer):
    """Serializer for Membership model."""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)

    class Meta:
        model = Membership
        fields = [
            'id', 'user', 'username', 'user_email', 'room', 'room_name',
            'role', 'joined_at', 'updated_at'
        ]
        read_only_fields = ['joined_at', 'updated_at']