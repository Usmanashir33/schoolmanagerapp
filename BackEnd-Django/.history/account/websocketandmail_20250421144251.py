from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

def signal_sender(destination,data):
    # print('signal start ',data['type'])
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        destination, # group name 
        data  # data must contain 'type' in it
    )
