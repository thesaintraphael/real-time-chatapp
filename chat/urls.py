from django.urls import path
from . import views as v

app_name = 'chat'

urlpatterns = [
    path('conversations', v.conversations, name='conversations'),
    path('<int:user_id>', v.create_conversation, name='create_conversation'),
    path('conversation/<int:conv_id>', v.room, name='room'),
    path('api/search-user', v.user_search, name='user-search'),

    # notifications
    path('notification/<int:notification_id>', v.notification_path, name='notification'),
    path('group/notification/<int:notification_id>/<str:code>', v.gr_notification_path, name='gr-notification'),
    path('api/notification/read_all', v.all_read, name='read_all'),

    # Groups
    path('api/create-group', v.create_group, name='create-group'),
    path('leave-group/<str:code>', v.leave_group, name='leave-group'),
    path('group/<str:code>', v.group_chat_room, name='group_chat_room'),

]
