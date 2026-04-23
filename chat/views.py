from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from rooms.models import Message, MessageReaction, MessageThread, Room
from .serializers import MessageSerializer, MessageReactionSerializer, MessageThreadSerializer


class IsRoomMember(permissions.BasePermission):
    """Permission to check if user is a member of the room."""
    
    def has_permission(self, request, view):
        room_id = view.kwargs.get('room_id') or view.kwargs.get('pk')
        if not room_id:
            return False
        
        try:
            room = Room.objects.get(id=room_id)
            return room.members.filter(id=request.user.id).exists()
        except Room.DoesNotExist:
            return False


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing chat messages."""
    
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsRoomMember]
    
    def get_queryset(self):
        """Get messages for the specified room."""
        room_id = self.kwargs.get('room_id')
        
        queryset = Message.objects.filter(
            room_id=room_id,
        ).select_related('sender', 'room').prefetch_related('reactions', 'threads')
        
        return queryset.order_by('created_at')
    
    def perform_create(self, serializer):
        """Create a new message."""
        room_id = self.kwargs.get('room_id')
        room = Room.objects.get(id=room_id)
        serializer.save(sender=self.request.user, room=room)
    
    @action(detail=True, methods=['post'])
    def react(self, request, pk=None):
        """Add a reaction to a message."""
        message = self.get_object()
        reaction = request.data.get('reaction')
        
        if not reaction:
            return Response(
                {'error': 'Reaction is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if reaction is valid
        valid_reactions = [choice[0] for choice in MessageReaction.REACTION_CHOICES]
        if reaction not in valid_reactions:
            return Response(
                {'error': f'Invalid reaction. Choose from: {", ".join(valid_reactions)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        message_reaction, created = MessageReaction.objects.get_or_create(
            message=message,
            user=request.user,
            reaction=reaction
        )
        
        if not created:
            # Toggle off if already exists
            message_reaction.delete()
            return Response({'status': 'reaction removed'})
        
        return Response(
            {'status': 'reaction added', 'reaction': reaction},
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['patch'])
    def edit(self, request, pk=None):
        """Edit a message."""
        message = self.get_object()
        
        if message.sender != request.user:
            return Response(
                {'error': 'You can only edit your own messages'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        content = request.data.get('content')
        if not content:
            return Response(
                {'error': 'Content is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        message.content = content
        message.is_edited = True
        message.save(update_fields=['content', 'is_edited', 'updated_at'])
        
        serializer = self.get_serializer(message)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def delete(self, request, pk=None):
        """Delete a message."""
        message = self.get_object()
        
        if message.sender != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You can only delete your own messages'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        message.delete()
        
        return Response({'status': 'message deleted'})
