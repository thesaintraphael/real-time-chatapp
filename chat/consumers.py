import json
from channels.generic.websocket import WebsocketConsumer
from .models import ConversationMessage, Conversation, Notification, GroupChat, GroupMessage, GroupNotification
from asgiref.sync import async_to_sync
from .serializers import NotificationSerializer
from channels.layers import get_channel_layer


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name


        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']

        content = message
        conversation_id = self.scope['url_route']['kwargs']['room_name']
        conversation = Conversation.objects.filter(id=conversation_id)[0]
        
        ConversationMessage.objects.create(conversation_id=conversation_id, content=content, created_bt=self.scope["user"])
        
        for user in conversation.users.all():
            if not user == self.scope['user']:
                to_user = user
            else:
                from_user = self.scope['user']

        notification = Notification.objects.create(to_user=to_user, created_by=from_user)

        notification_json = {
            'id': notification.id,
            'is_read': notification.is_read,
            'created_at': str(notification.created_at),
            'to_user': notification.to_user.username,
            'from_user': notification.created_by.username,
        }

        channel_layer = get_channel_layer()
        name = 'notification_' + str(to_user.id)
        async_to_sync(channel_layer.group_send)(
            name,
            {
                'type': 'pr_notify',
                'notification': notification_json,
            }
        )

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                # 'notification': notification_json,
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        username = event['username']
        # notification = event['notification']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            # 'notification': notification,
        }))


class PublicChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'group_%s' % self.room_name

        # Join Room
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()
    
    def disconnect(self, close_code):
        # Leave group code
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
    

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']

        content = message
        group_code = self.scope['url_route']['kwargs']['room_name']
        group = GroupChat.objects.filter(code=group_code)[0]

        GroupMessage.objects.create(group=group, content=content, created_by=self.scope["user"])
        # ------------------------------------------
            # Sending to Notification Socket

        for user in group.users.all():

            if user.id != self.scope['user'].id:

                notification = GroupNotification.objects.create(code=group_code, created_by=self.scope['user'], to_user=user)
                notification.save()

                notification_json = {
                    'id': notification.id,
                    'code': notification.code,
                    "group_name": group.name,
                    'is_read': notification.is_read,
                    'created_at': str(notification.created_at),
                    'to_user': user.username,
                    'from_user': notification.created_by.username,
                }

                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    str(user.id),
                    {
                        'type': 'notify',
                        'notification': notification_json, 
                    }
                )

        # ------------------------------------------

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'group_message',
                'message': message,
                'username': username,
            }
        )
    

    def group_message(self, event):
        message = event['message']
        username = event['username']

        self.send(text_data=json.dumps({
            'message': message,
            'username': username,
        }))


class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        if self.scope['user'].is_anonymous:
            self.close()
        
        else:
            self.group_name = str(self.scope['user'].id)
            async_to_sync(self.channel_layer.group_add)(
                self.group_name,
                self.channel_name
            )

            self.accept()

    def disconnect(self, close_code):
        self.close()
    

    def notify(self, event):

        notification = event['notification']
        self.send(text_data=json.dumps({
            'notification': notification
        }))


class PrivateNotifiactionConsumer(WebsocketConsumer):
    def connect(self):
        if self.scope['user'].is_anonymous:
            self.close()
        
        else:
            self.group_name = "notification_" + str(self.scope['user'].id)
            async_to_sync(self.channel_layer.group_add)(
                self.group_name,
                self.channel_name
            )

            self.accept()
    
    def disconnect(self, close_code):
        self.close()
    

    def pr_notify(self, event):
        notification = event['notification']
        self.send(text_data=json.dumps({
            'notification': notification
        }))