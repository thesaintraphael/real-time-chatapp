# Django Channels Real Time Chat App

This app allows users chatting in private chats and create group chats. Real time notification functionality is added to app.
User gets notifications any time someone writes hime or sends a message to groups user in

Repo mainly contains backend codes for the app. You can use it for better frontend


## Dependecies:
    pip install requirements.txt


## Run in Development:


1. #### Create at least two users:
    py manage.py createsuperuser


2. #### Install Docker and type the command in terminal:
    docker run -p 6379:6379 -d redis:5


3 #### Run the server:
    py manage.py runserver


Go to /conversations search for users or create a group to chat.

User Auth. and version for Development will be added soon
