from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [
    path('create-room/', views.CreateRoom.as_view({"post":"create"}), name="create-room"),
    path('list-rooms/', views.ListRooms.as_view(), name="list-rooms"),
]