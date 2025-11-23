from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

def signal_sender(d):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "chat_group",  # Replace with your group name
        {
            "type": "chat_message",
            "message": "Hello, this is a WebSocket message!"
        }
    )
