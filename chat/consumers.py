import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import random
import string


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.name = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

        self.accept()

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {"type": "joined.chat", "username": f"{self.name}"},
        )

    def chat_message(self, message):

        self.send(text_data=json.dumps({"username": self.name, "message": message}))

    def joined_chat(self, username):
        self.send(text_data=json.dumps({"message": f"{username} has joined the chat"}))
    
    def left_chat(self, username):
        self.send(text_data=json.dumps({"message": f"{username} has left the chat"}))

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
