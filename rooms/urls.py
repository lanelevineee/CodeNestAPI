from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RoomViewSet, JoinRoomView, LeaveRoomView, RoomMembersView, RoomSearchView,
    MessageViewSet, MessageReactionView, MessageThreadViewSet, RoomMessagesView
)

router = DefaultRouter()
router.register(r'', RoomViewSet, basename='room')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'threads', MessageThreadViewSet, basename='thread')

urlpatterns = [
    # Router URLs for CRUD operations
    path('', include(router.urls)),
    
    # Room actions
    path('<int:room_id>/join/', JoinRoomView.as_view(), name='join-room'),
    path('<int:room_id>/leave/', LeaveRoomView.as_view(), name='leave-room'),
    path('<int:room_id>/members/', RoomMembersView.as_view(), name='room-members'),
    path('<int:room_id>/messages/', RoomMessagesView.as_view(), name='room-messages'),
    
    # Message reactions
    path('messages/<int:message_id>/react/', MessageReactionView.as_view(), name='message-react'),
    path('messages/<int:message_id>/reactions/', MessageReactionView.as_view(), name='message-reactions'),
    
    # Search
    path('search/', RoomSearchView.as_view(), name='room-search'),
]
