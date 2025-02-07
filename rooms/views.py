from django.shortcuts import render
from rooms.models import Room, Membership
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import View, APIView
from rest_framework.viewsets import ModelViewSet
from rooms.serializer import RoomSerializer, MembershipSerializer
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.renderers import AdminRenderer, BrowsableAPIRenderer
class CreateRoom(ModelViewSet):
    serializer_class = RoomSerializer
    renderer_classes = [BrowsableAPIRenderer]
    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"message":"Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(creator=request.user)
            return Response({"message":f"Room {serializer.data['name']} created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class ListRooms(APIView):
    serializer_class = RoomSerializer
    queryset = Room.objects.all()
    renderer_classes = [AdminRenderer, BrowsableAPIRenderer]
    
    def get(self, request, *args, **kwargs):
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response({"rooms":serializer.data}, status=status.HTTP_200_OK)