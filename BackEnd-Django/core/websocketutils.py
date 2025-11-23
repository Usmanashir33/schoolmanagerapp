from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
import uuid


# def signal_sender(destination,data):
#     channel_layer = get_channel_layer()
#     async_to_sync(channel_layer.group_send)(
#         destination, # group name 
#         data  # data must contain 'type' in it
#     )
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
channel_layer = get_channel_layer()

def convert_uuid(obj):
    if isinstance(obj, dict):
        return {k: convert_uuid(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_uuid(i) for i in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_uuid(i) for i in obj)
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    return obj

def signal_sender(destination,data):
    # Make sure all UUIDs in the data dict are stringified
    safe_data = convert_uuid(data)
    async_to_sync(channel_layer.group_send)(
       destination, # group name 
        safe_data # data must contain 'type' in it
    )
