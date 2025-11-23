from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

def signal_sender(destination,data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"{destination}",
        data 
    )
