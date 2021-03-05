import chat.models
from django.contrib.auth.models import User
import string
import random



def fetch_notifications(user_id):
    
    user = User.objects.filter(id=user_id)
    notifications = chat.models.Notification.objects.filter(to_user=user_id, is_read=False)

    if notifications.exists():
        return notifications
    
    return None


def generate_unique_code():
    length = 6

    while True:
        code = ''.join(random.choices(string.ascii_letters, k=length))
        if not chat.models.GroupChat.objects.filter(code=code).exists():
            break
    
    return code


def fetch_gr_notifications(user):
    notifications = chat.models.GroupNotification.objects.filter(to_user=user, is_read=False)

    if notifications.exists():
        return notifications
    