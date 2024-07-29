from django.db.models.signals import post_save
from django.dispatch import receiver
from chat.models import Room
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@receiver(post_save, sender=Room)
def create_room(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        "allchats",         {
            "type": "chat.created",
            "room_name": instance.name,
        },
    )
        
