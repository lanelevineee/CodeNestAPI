from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .models import Room, Membership
from .serializer import RoomSerializer, MembershipSerializer


class CreateRoom(ModelViewSet):
    """ViewSet for creating and listing rooms."""
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Room.objects.filter(is_public=True)

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"message": "Unauthorized. Please login to create a room."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {
                "message": f"Room '{serializer.data['name']}' created successfully",
                "room": serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class ListRooms(APIView):
    """API View for listing all public rooms."""
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        rooms = Room.objects.filter(is_public=True).select_related('creator').prefetch_related('tags')
        serializer = RoomSerializer(rooms, many=True)
        return Response(
            {
                "count": rooms.count(),
                "rooms": serializer.data
            },
            status=status.HTTP_200_OK
        )


class MembershipViewSet(viewsets.ModelViewSet):
    """ViewSet for managing room memberships."""
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Membership.objects.all()
        return Membership.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)