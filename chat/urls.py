from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MessageViewSet

router = DefaultRouter()
router.register(r'rooms/(?P<room_id>\d+)/messages', MessageViewSet, basename='room-messages')

urlpatterns = [
    path('', include(router.urls)),
]
