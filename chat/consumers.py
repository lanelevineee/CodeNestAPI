import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from .models import Message, MessageThread, Room


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time chat functionality."""

    async def connect(self):
        """Handle WebSocket connection."""
        self.user = self.scope["user"]
        
        # Allow anonymous connections for public rooms
        if isinstance(self.user, AnonymousUser):
            # Try to authenticate via token in query params
            token = self.scope["query_string"].decode()
            if token.startswith("token="):
                token_value = token.split("=")[1]
                try:
                    access_token = AccessToken(token_value)
                    self.user = await self.get_user_from_token(access_token)
                except Exception:
                    await self.close()
                    return
        
        if not self.user.is_authenticated:
            await self.close()
            return

        # Get room_id from URL route
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name, 
            self.channel_name
        )

        await self.accept()
        
        # Send join notification
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "system_message",
                "message": f"{self.user.username} joined the chat",
                "timestamp": self.get_timestamp()
            }
        )

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'room_group_name'):
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            
            # Send leave notification
            if hasattr(self, 'user') and self.user.is_authenticated:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "system_message",
                        "message": f"{self.user.username} left the chat",
                        "timestamp": self.get_timestamp()
                    }
                )

    async def receive(self, text_data):
        """Receive message from WebSocket."""
        try:
            data = json.loads(text_data)
            message_type = data.get("type", "message")
            
            if message_type == "message":
                content = data.get("content", "").strip()
                if not content:
                    await self.send_error("Message content cannot be empty")
                    return

                # Save message to database
                message = await self.save_message(content)
                
                if message:
                    # Send message to room group
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "chat_message",
                            "message": {
                                "id": message.id,
                                "content": message.content,
                                "sender": {
                                    "id": message.sender.id,
                                    "username": message.sender.username,
                                    "email": message.sender.email
                                },
                                "timestamp": message.created_at.isoformat(),
                                "thread_id": message.thread.id if message.thread else None
                            }
                        }
                    )
            elif message_type == "typing":
                is_typing = data.get("is_typing", False)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "typing_indicator",
                        "user_id": self.user.id,
                        "username": self.user.username,
                        "is_typing": is_typing
                    }
                )
            elif message_type == "reaction":
                reaction = data.get("reaction")
                message_id = data.get("message_id")
                if reaction and message_id:
                    await self.handle_reaction(message_id, reaction)
                    
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON format")
        except Exception as e:
            await self.send_error(str(e))

    async def chat_message(self, event):
        """Send chat message to WebSocket."""
        await self.send(text_data=json.dumps(event["message"]))

    async def system_message(self, event):
        """Send system message to WebSocket."""
        await self.send(text_data=json.dumps({
            "type": "system",
            "message": event["message"],
            "timestamp": event["timestamp"]
        }))

    async def typing_indicator(self, event):
        """Send typing indicator to WebSocket."""
        await self.send(text_data=json.dumps({
            "type": "typing",
            "user_id": event["user_id"],
            "username": event["username"],
            "is_typing": event["is_typing"]
        }))

    async def reaction_update(self, event):
        """Send reaction update to WebSocket."""
        await self.send(text_data=json.dumps({
            "type": "reaction_update",
            "message_id": event["message_id"],
            "reactions": event["reactions"]
        }))

    async def send_error(self, message):
        """Send error message to WebSocket."""
        await self.send(text_data=json.dumps({
            "type": "error",
            "message": message
        }))

    @database_sync_to_async
    def get_user_from_token(self, token):
        """Get user from JWT token."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        return User.objects.get(id=token['user_id'])

    @database_sync_to_async
    def save_message(self, content):
        """Save message to database."""
        try:
            room = Room.objects.get(id=self.room_id)
            
            # Check if user is member of the room
            if not room.members.filter(id=self.user.id).exists():
                return None
            
            message = Message.objects.create(
                sender=self.user,
                room=room,
                content=content
            )
            return message
        except Room.DoesNotExist:
            return None
        except Exception as e:
            print(f"Error saving message: {e}")
            return None

    @database_sync_to_async
    def handle_reaction(self, message_id, reaction):
        """Handle message reaction."""
        try:
            from .models import MessageReaction
            message = Message.objects.get(id=message_id)
            
            # Toggle reaction
            existing = MessageReaction.objects.filter(
                message=message,
                user=self.user,
                reaction=reaction
            ).first()
            
            if existing:
                existing.delete()
            else:
                MessageReaction.objects.create(
                    message=message,
                    user=self.user,
                    reaction=reaction
                )
                
            # Send update to all users
            reactions = await self.get_message_reactions(message_id)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "reaction_update",
                    "message_id": message_id,
                    "reactions": reactions
                }
            )
        except Exception as e:
            print(f"Error handling reaction: {e}")

    @database_sync_to_async
    def get_message_reactions(self, message_id):
        """Get all reactions for a message."""
        from .models import MessageReaction
        reactions = MessageReaction.objects.filter(message_id=message_id)
        result = {}
        for r in reactions:
            if r.reaction not in result:
                result[r.reaction] = []
            result[r.reaction].append({
                "user_id": r.user.id,
                "username": r.user.username
            })
        return result

    def get_timestamp(self):
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
