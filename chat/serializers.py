from rest_framework import serializers
from rooms.models import Message, MessageReaction, MessageThread
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Simple user serializer for nested representations."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id', 'email']


class MessageReactionSerializer(serializers.ModelSerializer):
    """Serializer for message reactions."""
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = MessageReaction
        fields = ['id', 'user', 'reaction', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages."""
    
    sender = UserSerializer(read_only=True)
    room = serializers.PrimaryKeyRelatedField(read_only=True)
    reactions = MessageReactionSerializer(many=True, read_only=True)
    reply_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'room', 'content', 'created_at', 
            'updated_at', 'is_edited', 'reactions', 
            'reply_count'
        ]
        read_only_fields = ['id', 'sender', 'room', 'created_at', 'updated_at']
    
    def get_reply_count(self, obj):
        """Get count of replies to this message."""
        return obj.threads.count() if hasattr(obj, 'threads') else 0
    
    def create(self, validated_data):
        """Create a new message."""
        request = self.context.get('request')
        room = self.context.get('room')
        
        if not room:
            raise serializers.ValidationError("Room is required")
        
        validated_data['sender'] = request.user
        validated_data['room'] = room
        
        return super().create(validated_data)


class MessageThreadSerializer(serializers.ModelSerializer):
    """Serializer for message threads."""
    
    parent_message = MessageSerializer(read_only=True)
    message = MessageSerializer(read_only=True)
    
    class Meta:
        model = MessageThread
        fields = ['id', 'parent_message', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']
