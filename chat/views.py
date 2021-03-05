from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Conversation, ConversationMessage, Notification, GroupChat, GroupMessage, GroupNotification
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .serializers import SearchSerializer, UserSerializer, GroupChatSerializer
from django.http import JsonResponse
from .utils import fetch_notifications, fetch_gr_notifications



def index(request):
    return render(request, 'index.html')


@login_required(login_url='index')
def room(request, conv_id):
    if not Conversation.objects.filter(id=conv_id).exists():
        return redirect('index')


    conversation = Conversation.objects.filter(id=conv_id)[0]
    
    if not request.user in conversation.users.all():
        return redirect('chat:conversations')
    
    for user in conversation.users.all():
        if user != request.user:
            break
    
    chat_notifications =  Notification.objects.filter(created_by=user, to_user=request.user, is_read=False)
    if chat_notifications.exists():
        for notification in chat_notifications:
            notification.is_read = True
            notification.save()

    notifications = fetch_notifications(request.user.id)
    group_notifications = fetch_gr_notifications(request.user)
    
    context = {
        'room_name': conv_id,
        'conversation': conversation,
        'messages': conversation.messages.all(),
        'notifications': notifications,
        'gr_notifications': group_notifications
    }

    return render(request, 'chatroom.html', context)



@login_required(login_url='index')
def create_conversation(request, user_id):
    if not User.objects.filter(id=user_id).exists() or user_id == request.user.id:
        return redirect('index')

    conversations = Conversation.objects.filter(users__in=[request.user.id])
    conversations = conversations.filter(users__in=[user_id])

    if conversations.count() == 1:
        conversation = conversations[0]
        return redirect(reverse('chat:room', kwargs={'conv_id': conversation.id}))

    else:
        recipient = User.objects.get(pk=user_id)
        conversation = Conversation.objects.create()
        conversation.users.add(request.user)
        conversation.users.add(recipient)
        conversation.save()

        return redirect(reverse('chat:room', kwargs={'conv_id': conversation.id}))
    


@login_required(login_url='index')
def conversations(request):
    conversations = request.user.conversations.all()
    groups = request.user.group_chat.all()
    notifications = fetch_notifications(request.user.id)
    group_notifications = fetch_gr_notifications(request.user)

    number = 0
    if notifications:
        number = notifications.count()
    if group_notifications:
        number += group_notifications.count()

    context = {
        'conversations': conversations,
        'groups': groups,
        'notifications': notifications,
        'gr_notifications': group_notifications,
        'number': number,
    }

    return render(request, 'conversations.html', context)


@api_view(['POST'])
def user_search(request):
    serializer = SearchSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()

        users = list(User.objects.filter(username__icontains=serializer.data['search']))
        serializer2 = UserSerializer(users, many=True)
        return Response(serializer2.data)
    
    return Response(serializer.errors)


def notification_path(request, notification_id):
    if not Notification.objects.filter(id=notification_id).exists():
        return redirect('chat:conversations')
    
    notification = Notification.objects.filter(id=notification_id)[0]
    
    conversations = Conversation.objects.filter(users__in=[notification.created_by])
    conversations = conversations.filter(users__in=[notification.to_user])

    if conversations.count() == 1:
        conversation = conversations[0]
        notification.is_read = True
        notification.save()
        return redirect(reverse('chat:room', kwargs={'conv_id': conversation.id}))
    
    return redirect('chat:conversation')



def gr_notification_path(request, notification_id, code):
    if not GroupNotification.objects.filter(id=notification_id, code=code).exists():
        return redirect('chat:conversations')
    
    notification = GroupNotification.objects.get(id=notification_id, to_user=request.user)

    notification.is_read=True
    notification.save()

    return redirect(reverse('chat:group_chat_room', kwargs={'code': code}))



@login_required(login_url='index')
@api_view(['POST'])
def create_group(request):
    serializer = GroupChatSerializer(data=request.data)
    print(serializer)

    if serializer.is_valid():
        serializer.save()
    
        return Response(serializer.data)

    return Response(serializer.errors)


def group_chat_room(request, code):
    
    if not GroupChat.objects.filter(code=code).exists():
        return redirect('chat:conversations')
    
    groups = GroupChat.objects.filter(code=code)

    if not groups.filter(users__in=[request.user.id]).exists():
        groups[0].users.add(request.user)
        groups[0].save()
    
    group = groups[0]

    chat_notifications = GroupNotification.objects.filter(code=code, to_user=request.user, is_read=False)
    if chat_notifications.exists():
        for notification in chat_notifications:
            notification.is_read = True
            notification.save()

    notifications = fetch_notifications(request.user.id)
    group_notifications = fetch_gr_notifications(request.user)

    context ={
        'room_name': code,
        'group': group,
        'messages': group.group_messages.all(),
        'notifications':  notifications,
        'gr_notifications':  group_notifications,
    }

    return render(request, 'group_chat.html', context)



def leave_group(request, code):
    if not GroupChat.objects.filter(code=code).exists():
        return redirect('chat:conversations')
    
    groups = GroupChat.objects.filter(code=code, users__in=[request.user.id])

    if groups.exists():
        group = groups[0]
        group.users.remove(request.user)
        group.save()
        if group.users.all().count() == 0:
            group.delete()

        # TODO  MESSAGES 
    
    return redirect('chat:conversations')
    

@login_required(login_url='index')
@api_view(['GET'])
def all_read(request):
    
    private_notifications = list(Notification.objects.filter(to_user=request.user))
    gr_notifications = list(GroupNotification.objects.filter(to_user=request.user))

    notifications = gr_notifications + private_notifications

    for notification in notifications:
        notification.is_read = True
        notification.save()
    
    return Response({'message': 'All notifications marked as read.'}, status=status.HTTP_200_OK)