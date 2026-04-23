from rest_framework import serializers
from .models import Room, Membership, Tag, Message, MessageReaction, MessageThread


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


class MessageReactionSerializer(serializers.ModelSerializer):
    """Serializer for MessageReaction model."""
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = MessageReaction
        fields = ['id', 'reaction', 'user', 'user_username', 'created_at']
        read_only_fields = ['user', 'created_at']


class MessageThreadSerializer(serializers.ModelSerializer):
    """Serializer for MessageThread model."""
    message_data = serializers.SerializerMethodField()

    class Meta:
        model = MessageThread
        fields = ['id', 'parent_message', 'message', 'message_data', 'created_at']
        read_only_fields = ['message', 'created_at']

    def get_message_data(self, obj):
        if obj.message:
            return MessageSerializer(obj.message, context=self.context).data
        return None


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model with reactions and thread info."""
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    sender_avatar = serializers.SerializerMethodField()
    reactions = MessageReactionSerializer(many=True, read_only=True)
    reaction_count = serializers.SerializerMethodField()
    has_thread = serializers.SerializerMethodField()
    thread_count = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id', 'room', 'sender', 'sender_username', 'sender_avatar',
            'content', 'created_at', 'updated_at', 'is_edited',
            'reactions', 'reaction_count', 'has_thread', 'thread_count'
        ]
        read_only_fields = ['sender', 'created_at', 'updated_at', 'is_edited']

    def get_sender_avatar(self, obj):
        request = self.context.get('request')
        if obj.sender.profile.avatar and request:
            return request.build_absolute_uri(obj.sender.profile.avatar.url)
        return None

    def get_reaction_count(self, obj):
        return obj.reactions.count()

    def get_has_thread(self, obj):
        return hasattr(obj, 'thread')

    def get_thread_count(self, obj):
        return obj.threads.count()