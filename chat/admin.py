from django.contrib import admin
from rooms.models import Message, MessageReaction, MessageThread


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin configuration for Message model."""
    
    list_display = ['id', 'sender', 'room', 'content_preview', 'created_at', 'is_edited']
    list_filter = ['room', 'is_edited', 'created_at']
    search_fields = ['content', 'sender__username', 'room__name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    raw_id_fields = ['sender', 'room']
    
    def content_preview(self, obj):
        """Show preview of message content."""
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):
    """Admin configuration for MessageReaction model."""
    
    list_display = ['id', 'message', 'user', 'reaction', 'created_at']
    list_filter = ['reaction', 'created_at']
    search_fields = ['message__content', 'user__username']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    raw_id_fields = ['message', 'user']


@admin.register(MessageThread)
class MessageThreadAdmin(admin.ModelAdmin):
    """Admin configuration for MessageThread model."""
    
    list_display = ['id', 'parent_message', 'message', 'created_at']
    list_filter = ['created_at']
    search_fields = ['parent_message__content', 'message__content']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    raw_id_fields = ['parent_message', 'message']
