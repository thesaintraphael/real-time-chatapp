from django.contrib import admin
from .models import *



class NotificationAdmin(admin.ModelAdmin):
    list_dsiplay = ['created_by', 'to_user', 'is_read', 'created_at']
    list_dsiplay_links = ['created_by']
    list_filter = ['is_read', 'created_at']



admin.site.register(Conversation)
admin.site.register(ConversationMessage)
admin.site.register(Search)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(GroupChat)
admin.site.register(GroupMessage)
admin.site.register(GroupNotification)
