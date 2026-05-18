import json
import os
from pathlib import Path
import uuid

import cv2
import numpy as np
from deepface import DeepFace

from django.conf import settings

from .serializers import DeviceSerializer
from core.websocketutils import signal_sender
from .face_engine import model,model_name

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.files.base import ContentFile
from django.db.models import Q
from rest_framework_simplejwt.tokens import UntypedToken
from authUser.models import User
from authUser.serializers import MiniUserSerializer
from teacher.serializers import MiniTeacherSerializer
from student.serializers import MiniStudentSerializer
from staff.serializers import MiniStaffSerializer
from school.models import School
from .models import Device


class FaceDetectionConsumer(AsyncWebsocketConsumer) :
    #connection to the websocket
    async def connect(self):
        token = self.scope.get('query_string').decode().split('token=')[1]
        self.user = await get_user_by_token(token)
        if self.user.role.lower() in ['staff','director'] : # only staff and director  can connect to the face detection websocket
            self.user_id = self.user.id
            self.user_room = f"face_room{self.user_id}" # itll be unique for every user 
            print('self.user_room Detection : ', self.user_room)
            await self.channel_layer.group_add(
                self.user_room, self.channel_name
            )
            await self.accept()
            # print(f"face detection connected  :{self.user_id,self.user.username} ")
        else :
            await self.close()
        # self.face_cascade = cv2.CascadeClassifier(
        #     cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        # )
        # self.trackers = []
        # self.model = model()
        
    # disconnection to the websocket
    async def disconnect(self, code):
       await self.channel_layer.group_discard(
           self.user_room, self.channel_name
       )

    async def receive(self, text_data=None, bytes_data=None):
        if not bytes_data:
            return

        # ✅ Decode image properly
        img_array = np.frombuffer(bytes_data, np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if frame is None:
            print("❌ Frame decode failed")
            return

        # ✅ Resize (VERY IMPORTANT for DeepFace)
        # frame = cv2.resize(frame, (480, 360))

        # ✅ Frame counter
        if not hasattr(self, "frame_count"):
            self.frame_count = 0
        self.frame_count += 1

        try:
            faces = DeepFace.extract_faces(
                img_path = frame ,
                detector_backend="opencv",
                enforce_detection = False ,
                anti_spoofing = True
            )
            if len(faces) > 0:
                face = faces[-1]
                # print('face: ', face)
                face.pop('face')  # Remove the actual face image data to reduce payload size

                # ✅ Confidence check
                if face['confidence'] > 0.6 :
                    await self.send(json.dumps({
                        'type': 'face_detection',
                        "detected": True,
                        "face_data": face ,
                    }))
                    return 
                await self.send(json.dumps({
                    'type': 'face_detection',
                    "detected": False
                })) 

        except Exception as e:
            print("❌ DeepFace error:", e)
                               
                
    async def send_response(self,data) :
        # sending to websocket 
        await self.send(json.dumps(data, cls=UUIDEncoder))

class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)  # Convert UUID to string
        return super().default(obj)


    
class DeviceConsumer(AsyncWebsocketConsumer) :
    #connection to the websocket
    async def connect(self):
        school = self.scope['url_route']['kwargs']['schoolId']
        device = self.scope['url_route']['kwargs']['deviceId']
        self.school = await get_school_by_Id(school)
        self.device  = await get_school_device_by_Id(self.school.id,device)
        self.room_name = self.device.id if self.device else None
        self.faces_db = os.path.join(settings.MEDIA_ROOT, 'faces_frames')
        print('self.faces_db Recognizer : ', self.faces_db)
        self.model = model() # load the model once when the consumer connects, so it can be reused for all frames without reloading (Facenet)
        self.model_name = model_name
        if self.school and self.device :  # device found and match 
            if not self.device.status == 'Active' : # if device is not active then disconnect it
                await update_device_connectivity(
                    self.school.id,device,
                    "Disconnected"
                )
                await self.close()
                return 
            await self.channel_layer.group_add(
                self.room_name, self.channel_name
            )
            await self.accept()
            #check device connectivity and update it to connected
            await update_device_connectivity(
                self.school.id,device,
                "Connected" 
            )
        else :
            await self.close()
        
    # disconnection to the websocket
    async def disconnect(self, code):
        await update_device_connectivity(
            self.school.id,self.device.id,
            "Disconnected"
        )
        await self.channel_layer.group_discard(
           self.room_name, self.channel_name
       )
    #---------------------------------------------------------------------------------------
    #                  ATTENDANCE SIGNALS FOR TEACHERS AND STAFFS 
    #---------------------------------------------------------------------------------------
    async def receive(self, text_data=None, bytes_data=None):
        # print("school",self.school)
        # print("device",self.device)
        if bytes_data: # camera stream data (face detection)
            # ✅ Decode image properly
            img_array = np.frombuffer(bytes_data, np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR) 
            if frame is None:
                print("❌ Frame decode failed")
                return
            

            if frame is None:
                await self.send(json.dumps({
                    'type': 'face_recognition',
                    'detected': False,
                }))
                return 
                
            # ✅ Resize (VERY IMPORTANT for DeepFace)
            frame = cv2.resize(frame, (480, 360))
            # cv2.imwrite("DBG222222.jpg", frame) 
           
            try:
                resp = await recognize_face(self,frame)
                print('resp: ', resp)   
                if resp and resp['detected'] :
                    role_user = await get_user_role_by_user_id(resp['user_id'])
                    print('role_user', role_user) 
                    if role_user : # serialize user data 
                        # implement the logic here for that user 
                        pass 
                        await self.send(json.dumps({
                            'type': 'face_detection',
                            # 'type': 'face_recognition',
                            "detected": True,
                            "userDetails": role_user ,
                        }))
                        return 
                        
                    else :
                        await self.send(json.dumps({
                            'type': 'face_detection',
                            # 'type': 'face_recognition',
                            "detected": False
                        })) 
                        return 
                await self.send(json.dumps({
                    'type': 'face_detection',
                    # 'type': 'face_recognition',
                    "detected": False
                })) 
            except Exception as e:
                print("❌ DeepFace errors:", e) 
    

@database_sync_to_async
def get_user_by_token(token) : 
    try :
        decoded = UntypedToken(token).payload
        user_id = decoded.get('user_id')
        user = User.objects.get(id = user_id)
        return user if user else None
    except :
        return None 
@database_sync_to_async    
def get_user_role_by_user_id(user_id) : 
    try :
        user = User.objects.filter(id = user_id).first()
        # user_role = user.role.lower()
        # get user role data 
        student = hasattr(user,'student')
        if student :
            return MiniStudentSerializer(user.student).data
        
        teacher = hasattr(user,'teacher')
        if teacher :
            return MiniTeacherSerializer(user.teacher).data
        
        staff = hasattr(user,'staff') 
        if staff :
            return MiniStaffSerializer(user.staff).data
        
        return None
    except :
        return None 
    
@database_sync_to_async    
def get_school_by_Id(schoolId) : 
    try :
        school = School.objects.get(id = schoolId)
        return school if school else None
    except :
        return None 
    
@database_sync_to_async    
def get_school_device_by_Id(school_id,deviceId) : 
    try :
        device = Device.objects.filter(
            id = deviceId,
            school__id = school_id
        ).first()
        return device if device else None
    except :
        return None 
    
@database_sync_to_async    
def update_device_connectivity(school_id,deviceId,connectivity) : 
    try :
        device = Device.objects.filter(
            id = deviceId,
            school__id = school_id
        ).first() 
        if device :
            device.connectivity = connectivity
            device.save()
            # serialize device and send it to the room
            device_data = DeviceSerializer(device).data
            destination_name = f"school-{school_id}"
            signal_data = {
                'type' : "school_feeder" ,
                'signalType' :"deviceConnectivity",
                'signalData' :device_data
            }
            signal_sender(destination_name,signal_data)
        return True if device else False 
    except :
        return None 

async def recognize_face (self, frame):
    results= DeepFace.find(
        frame, 
        db_path = self.faces_db , 
        model_name = "Facenet" , 
        enforce_detection = False,
        refresh_database =True
        )
    if len(results) > 0 and len(results[0]) > 0:
        best = results[0].iloc[0]
        if best["distance"] < 0.5 and best["confidence"] > 85  :
            identity = best["identity"]
            name = Path(identity).stem.split("_")[-1]  # to grab the user ID from the path 
            return {
                "detected" :True,
                "user_id": name ,
                "confidence": best["confidence"],
            }
        return {
            'detected':False
        }
        
    return None