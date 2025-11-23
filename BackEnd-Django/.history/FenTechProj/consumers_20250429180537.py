import json
import uuid

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.files.base import ContentFile
from django.db.models import Q
from rest_framework_simplejwt.tokens import UntypedToken
from authUser.models import User


class FentchConsumer(AsyncWebsocketConsumer) :
    #connection to the websocket
    async def connect(self):
        token = self.scope.get('query_string').decode().split('token=')[1]
        self.user = await get_user_by_token(token)
        if self.user :
            self.user_id = self.user.id
            self.user_room = f"room{self.user_id}" # itll be unique for every user 
            print('self.user_room: ', self.user_room)
            # print('self.user_room: ', self.user_room)
            await self.channel_layer.group_add(
                self.user_room, self.channel_name
            )
            await self.accept()
            print(f"connected  :{self.user_id,self.user.username} ")
        else :
            await self.close()
        
    # disconnection to the websocket
    async def disconnect(self, code):
       await self.channel_layer.group_discard(
           self.user_room, self.channel_name
       )
       print('disconnected')
        
    # receiving data after connection
    async def receive(self, bytes_data=None, text_data=None):
        if text_data :
            data = json.loads(text_data)
            # print(text_data)
            
            # if data['status'] == 'message' and data['withFile']: # the file is sent
                # self.message_data = data
            
                # self.friend_id =data['friend_id'] # imean frd here its mis use 
                # self.friend_rm = f"chat_room{self.friend_id}"
                # messageDetails ={
                #     "friend_id" : self.friend_id ,
                #     'user_id': self.user_id,
                #     'message_id' : data['message_id']
                # }
                # # message = await deleteMessageForAll(messageDetails)
                # if 'message' :
                #     delResponse = {
                #         'type':'senderFunction',
                #         'status' :'deleteMessageForAll',
                #         'response' : 'message'
                #     }
                #     # send it only to the message sender
                #     await self.channel_layer.group_send(
                #         self.friend_rm , delResponse
                #     )
                #     await self.channel_layer.group_send(
                #         self.user_room , delResponse
                #     )
                
    async def send_response(self,data) :
        print('sending response to websocket',data)
        # sending to websocket 
        await self.send(json.dumps(data, cls=UUIDEncoder))


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)  # Convert UUID to string
        return super().default(obj)

@database_sync_to_async    
def get_user_by_token(token) :
    try :
        decoded = UntypedToken(token).payload
        user_id = decoded.get('user_id')
        user = User.objects.get(id = user_id)
        return user if user else None
    except :
        return None 