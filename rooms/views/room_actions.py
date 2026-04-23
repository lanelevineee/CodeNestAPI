from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from django.db.models import Q
from django.shortcuts import get_object_or_404
from ..models import Room, Membership, Tag
from ..serializer import RoomSerializer, MembershipSerializer


class RoomViewSet(viewsets.ModelViewSet):
    """ViewSet for CRUD operations on rooms."""
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Room.objects.filter(
                Q(is_public=True) | Q(memberships__user=user)
            ).distinct().select_related('creator').prefetch_related('tags')
        return Room.objects.filter(is_public=True).select_related('creator').prefetch_related('tags')

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)
        room = serializer.instance
        Membership.objects.create(user=self.request.user, room=room, role='moderator')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.is_public and not (
            request.user.is_authenticated and 
            (request.user == instance.creator or Membership.objects.filter(user=request.user, room=instance).exists())
        ):
            return Response({'error': 'You do not have permission to access this room'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if not (request.user == instance.creator or Membership.objects.filter(user=request.user, room=instance, role='moderator').exists()):
            return Response({'error': 'Only creator or moderators can update this room'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'message': 'Room updated successfully', 'room': serializer.data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance.creator:
            return Response({'error': 'Only the creator can delete this room'}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response({'message': 'Room deleted successfully'}, status=status.HTTP_200_OK)


class JoinRoomView(APIView):
    """API View for joining a room."""
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        room = get_object_or_404(Room, pk=room_id)
        if not room.is_public:
            return Response({'error': 'Cannot join private rooms directly'}, status=status.HTTP_403_FORBIDDEN)
        if Membership.objects.filter(user=request.user, room=room).exists():
            return Response({'message': 'You are already a member of this room'}, status=status.HTTP_400_BAD_REQUEST)
        Membership.objects.create(user=request.user, room=room, role='member')
        return Response({
            'message': 'Successfully joined ' + room.name,
            'membership': {'room_id': room.id, 'room_name': room.name, 'role': 'member'}
        }, status=status.HTTP_201_CREATED)


class LeaveRoomView(APIView):
    """API View for leaving a room."""
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        room = get_object_or_404(Room, pk=room_id)
        if request.user == room.creator:
            return Response({'error': 'Creator cannot leave the room'}, status=status.HTTP_400_BAD_REQUEST)
        membership = Membership.objects.filter(user=request.user, room=room).first()
        if not membership:
            return Response({'message': 'You are not a member of this room'}, status=status.HTTP_400_BAD_REQUEST)
        membership.delete()
        return Response({'message': 'Successfully left ' + room.name}, status=status.HTTP_200_OK)


class RoomMembersView(APIView):
    """API View for listing room members."""
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, room_id):
        room = get_object_or_404(Room, pk=room_id)
        if not room.is_public and not (
            request.user.is_authenticated and 
            (request.user == room.creator or Membership.objects.filter(user=request.user, room=room).exists())
        ):
            return Response({'error': 'You do not have permission to access this room'}, status=status.HTTP_403_FORBIDDEN)
        memberships = Membership.objects.filter(room=room).select_related('user__profile')
        return Response({
            'count': memberships.count(),
            'members': [{
                'id': m.user.id, 'username': m.user.username, 'email': m.user.email,
                'firstName': m.user.firstName, 'lastName': m.user.lastName,
                'avatar': request.build_absolute_uri(m.user.profile.avatar.url) if m.user.profile.avatar else None,
                'role': m.role, 'joined_at': m.joined_at
            } for m in memberships]
        }, status=status.HTTP_200_OK)


class RoomSearchView(APIView):
    """API View for searching rooms."""
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '')
        tag = request.query_params.get('tag', '')
        rooms = Room.objects.filter(is_public=True).select_related('creator').prefetch_related('tags')
        if query:
            rooms = rooms.filter(Q(name__icontains=query) | Q(description__icontains=query))
        if tag:
            rooms = rooms.filter(tags__name__icontains=tag)
        rooms = rooms.distinct()[:50]
        return Response({
            'count': rooms.count(),
            'rooms': RoomSerializer(rooms, many=True, context={'request': request}).data
        }, status=status.HTTP_200_OK)
