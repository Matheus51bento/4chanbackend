import json
from channels.generic.websocket import WebsocketConsumer
from chat.models import Room
from asgiref.sync import async_to_sync
import random
import string
from datetime import datetime

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]

        if not Room.objects.filter(name=self.room_name).exists():
            self.close()

        self.room_group_name = f"chat_{self.room_name}"

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.name = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

        self.accept()

        self.send(text_data=json.dumps({"user_info": f"{self.name}"}))

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "joined.chat", "username": f"{self.name}"},
        )

    def chat_message(self, message):
        actual_date = str(datetime.now())
        self.send(text_data=json.dumps({"username": self.name, "message": message, "date": actual_date}))

    def joined_chat(self, username):
        name = username["username"]
        actual_date = str(datetime.now())
        self.send(text_data=json.dumps({"joined": f"{name} has joined the chat", "date": actual_date}))
    
    def left_chat(self, username):
        name = username["username"]
        actual_date = str(datetime.now())
        self.send(text_data=json.dumps({"left": f"{name} has left the chat", "date": actual_date}))

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {"type": "left.chat", "username": f"{self.name}"},
        )
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat.message", "message": message}
        )


class ChatListConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        async_to_sync(self.channel_layer.group_add)(
            "allchats", self.channel_name
        )

        chats = Room.objects.all()
        response = []
        for chat in chats:
            response.append({"room": chat.name})
        self.send(text_data=json.dumps({"rooms":response}))

    def chat_created(self, room_name):
        actual_date = str(datetime.now())
        self.send(text_data=json.dumps({"room": room_name["room_name"], "date": actual_date}))

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            "allchats", self.channel_name
        )

    def receive(self, text_data):
        room_name = json.loads(text_data)["room_name"]
        Room.objects.create(name=room_name)