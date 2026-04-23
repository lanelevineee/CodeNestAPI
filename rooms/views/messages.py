from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from django.db.models import Count
from ..models import Message, MessageReaction, MessageThread, Room, Membership
from ..serializer import MessageSerializer, MessageReactionSerializer, MessageThreadSerializer


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for CRUD operations on messages."""
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        room_id = self.request.query_params.get('room_id')
        if room_id:
            room = get_object_or_404(Room, pk=room_id)
            # Check if user has access to the room
            if not room.is_public and not (
                self.request.user == room.creator or 
                Membership.objects.filter(user=self.request.user, room=room).exists()
            ):
                return Message.objects.none()
            return Message.objects.filter(room=room).select_related(
                'sender', 'sender__profile'
            ).prefetch_related('reactions', 'threads').order_by('-created_at')
        return Message.objects.none()

    def perform_create(self, serializer):
        room_id = self.request.data.get('room')
        room = get_object_or_404(Room, pk=room_id)
        
        # Check if user is a member of the room (or creator)
        if not (
            self.request.user == room.creator or 
            Membership.objects.filter(user=self.request.user, room=room).exists()
        ):
            raise Exception('You are not a member of this room')
        
        serializer.save(sender=self.request.user)


class MessageReactionView(APIView):
    """API View for adding/removing message reactions."""
    permission_classes = [IsAuthenticated]

    def post(self, request, message_id):
        message = get_object_or_404(Message, pk=message_id)
        reaction = request.data.get('reaction')
        
        if not reaction:
            return Response({'error': 'Reaction is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user has access to the message's room
        room = message.room
        if not room.is_public and not (
            request.user == room.creator or 
            Membership.objects.filter(user=request.user, room=room).exists()
        ):
            return Response({'error': 'You do not have permission to react to this message'}, status=status.HTTP_403_FORBIDDEN)
        
        # Create or toggle reaction
        existing_reaction = MessageReaction.objects.filter(
            message=message, user=request.user, reaction=reaction
        ).first()
        
        if existing_reaction:
            existing_reaction.delete()
            return Response({'message': 'Reaction removed'}, status=status.HTTP_200_OK)
        else:
            MessageReaction.objects.create(message=message, user=request.user, reaction=reaction)
            return Response({'message': 'Reaction added'}, status=status.HTTP_201_CREATED)

    def get(self, request, message_id):
        message = get_object_or_404(Message, pk=message_id)
        reactions = MessageReaction.objects.filter(message=message).select_related('user')
        return Response({
            'count': reactions.count(),
            'reactions': MessageReactionSerializer(reactions, many=True, context={'request': request}).data
        }, status=status.HTTP_200_OK)


class MessageThreadViewSet(viewsets.ModelViewSet):
    """ViewSet for managing message threads."""
    serializer_class = MessageThreadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        parent_message_id = self.request.query_params.get('parent_message_id')
        if parent_message_id:
            parent_message = get_object_or_404(Message, pk=parent_message_id)
            room = parent_message.room
            
            # Check if user has access to the room
            if not room.is_public and not (
                self.request.user == room.creator or 
                Membership.objects.filter(user=self.request.user, room=room).exists()
            ):
                return MessageThread.objects.none()
            
            return MessageThread.objects.filter(
                parent_message=parent_message
            ).select_related('message__sender', 'message__sender__profile').order_by('created_at')
        return MessageThread.objects.none()

    def perform_create(self, serializer):
        parent_message_id = self.request.data.get('parent_message')
        parent_message = get_object_or_404(Message, pk=parent_message_id)
        room = parent_message.room
        
        # Check if user is a member of the room
        if not (
            self.request.user == room.creator or 
            Membership.objects.filter(user=self.request.user, room=room).exists()
        ):
            raise Exception('You are not a member of this room')
        
        # Create the thread message first
        content = self.request.data.get('content')
        if not content:
            raise Exception('Content is required for thread message')
        
        thread_message = Message.objects.create(
            room=room, sender=self.request.user, content=content
        )
        
        serializer.save(parent_message=parent_message, message=thread_message)


class RoomMessagesView(APIView):
    """API View for getting all messages in a room with pagination."""
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, room_id):
        room = get_object_or_404(Room, pk=room_id)
        
        # Check if user has access to the room
        if not room.is_public and not (
            request.user.is_authenticated and (
                request.user == room.creator or 
                Membership.objects.filter(user=request.user, room=room).exists()
            )
        ):
            return Response({'error': 'You do not have permission to access this room'}, status=status.HTTP_403_FORBIDDEN)
        
        # Get pagination params
        limit = int(request.query_params.get('limit', 50))
        offset = int(request.query_params.get('offset', 0))
        
        messages = Message.objects.filter(room=room).select_related(
            'sender', 'sender__profile'
        ).prefetch_related('reactions', 'threads').order_by('-created_at')[offset:offset+limit]
        
        return Response({
            'count': Message.objects.filter(room=room).count(),
            'limit': limit,
            'offset': offset,
            'messages': MessageSerializer(messages, many=True, context={'request': request}).data
        }, status=status.HTTP_200_OK)
