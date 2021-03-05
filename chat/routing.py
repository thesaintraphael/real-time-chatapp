from django.urls import re_path, path
from . import consumers as con


websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', con.ChatConsumer.as_asgi()),
    path('ws/chat/group/<str:room_name>/', con.PublicChatConsumer.as_asgi()),
    re_path(r'notifications/$', con.NotificationConsumer.as_asgi()),
    path('ws/private/', con.PrivateNotifiactionConsumer.as_asgi())

] 