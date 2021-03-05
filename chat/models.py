from django.db import models
from django.contrib.auth.models import User
from .utils import generate_unique_code
# from django.db.models.signals import post_save
# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync


class Conversation(models.Model):
    users = models.ManyToManyField(User, related_name='conversations')
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-modified_at']


class ConversationMessage(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    content  = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_bt = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)

    class Meta:
        ordering = ['created_at']

    def save(self, *args, **kwargs):
        self.conversation.save()

        super(ConversationMessage, self).save(*args, **kwargs)


class Search(models.Model):
    search = models.CharField(max_length=250)
    
    def __str__(self):
        return self.search


class Notification(models.Model):
    to_user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='creatednotifications', on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_at']



class GroupChat(models.Model):
    code = models.CharField(max_length=8, unique=True, default=generate_unique_code)
    name = models.CharField(max_length=16, default='(Group)')
    users = models.ManyToManyField(User, related_name='group_chat')
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-modified_at']


class GroupMessage(models.Model):
    group = models.ForeignKey(GroupChat, related_name='group_messages', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='group_messages', on_delete=models.CASCADE)

    class Meta:
        ordering = ['created_at']
    
    def save(self, *args, **kwargs):
        self.group.save()
        
        super(GroupMessage, self).save(*args, **kwargs)


class GroupNotification(models.Model):
    code = models.CharField(max_length=8)
    is_read = models.BooleanField(default=False)
    to_user = models.ForeignKey(User, related_name='group_notification', on_delete=models.CASCADE, default=1)
    created_by = models.ForeignKey(User, related_name='created_group_notification', on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code
    
    class Meta:
        ordering = ['-created_at']
