import json
import uuid
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.files.base import ContentFile
from django.db.models import Q
from rest_framework_simplejwt.tokens import UntypedToken
from authUser.models import User
from school.models import School
from urllib.parse import parse_qs

class AppConsumer(AsyncWebsocketConsumer) :
    #connection to the websocket
    async def connect(self):
        query_params = parse_qs(self.scope["query_string"].decode())
        token = query_params.get("token", [None])[0] # Get the token from query parameters
        self.user = await get_user_by_token(token)
        if self.user :
            self.user_id = self.user.id
            self.user_room = f"room{self.user_id}" # itll be unique for every user 
            await self.channel_layer.group_add(
                self.user_room, self.channel_name
            )
            await self.accept()
            print("app use handshecked ")
        else :
            await self.close()
        
    # disconnection to the websocket
    async def disconnect(self, code):
       await self.channel_layer.group_discard(
           self.user_room, self.channel_name
       )
        
    # receiving data after connection
    async def receive(self, bytes_data=None, text_data=None):
        if text_data :
            data = json.loads(text_data)
                
    # sending to websocket  in the front end 
    async def send_response1(self,event) :
        await self.send(json.dumps(event,cls=UUIDEncoder))

class SchoolConsumer(AsyncWebsocketConsumer) :
    #connection to the websocket
    async def connect(self):
        school = self.scope['url_route']['kwargs']['schoolId']
        self.school = await get_school_by_Id(school)
        if self.school :
            self.school_room = f"school-{self.school.id}" # itll be unique for every school
            await self.channel_layer.group_add(
                self.school_room, self.channel_name
            )
            await self.accept()
            
        else :
            await self.close()
            
            
    # disconnection to the websocket
    async def disconnect(self, code):
        await self.channel_layer.group_discard(
           self.school_room, self.channel_name
        )
        
    # receiving data after connection
    async def receive(self, bytes_data=None, text_data=None):
        if text_data :
            data = json.loads(text_data)
               
    async def school_feeder(self,event) :
        # sending to websocket 
        await self.send(json.dumps({
            "signalType": event.get("signalType"),
            "updatedDeviceData": event.get("signalData")
        }, cls=UUIDEncoder))
        
    async def school_feeder2(self,event) :
        await self.send(json.dumps(event, cls=UUIDEncoder))

class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)  # Convert UUID to string
        return super().default(obj)


@database_sync_to_async    
def get_school_by_Id(schoolId) : 
    try :
        school = School.objects.get(id = schoolId)
        return school if school else None
    except :
        return None 
    
@database_sync_to_async    
def get_user_by_token(token) : 
    try :
        decoded = UntypedToken(token).payload
        user_id = decoded.get('user_id')
        user = User.objects.get(id = user_id)
        return user if user else None
    except :
        return None 