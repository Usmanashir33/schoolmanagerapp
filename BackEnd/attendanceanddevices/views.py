import json

from django.shortcuts import render

from .utils import recognize_face

from .serializers import BiometricIdentitySerializer, DeviceSerializer, UpdateBiometricIdentitySerializer
from .models import BiometricIdentity
from .models import User
from school.models import School
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser,FormParser
from core.permissions import DirectorUserPermission

# Create your views here.
class FaceDetectionView(APIView) :
    # parser_classes =[MultiPartParser,FormParser]
    permission_classes=[
        permissions.IsAuthenticated,
        DirectorUserPermission,
    ]
    
    def post(self, request ) : 
        try:
            faces = recognize_face(request)
            return Response({"success":"Face Detected","FaceData":faces}, status=status.HTTP_201_CREATED)
        except:
            return Response({"error":"server error"},status=status.HTTP_200_OK) 
        
class BiometricIdentityView(APIView) :
    parser_classes =[MultiPartParser,FormParser]
    permission_classes=[
        permissions.IsAuthenticated,
        DirectorUserPermission,
    ]
    
    def get(self, request, school_id): 
        try:
            director = request.user.director
             # validate director actions  on his school only
            school = School.objects.filter(director_id = director.id, id=school_id).first()  #.exists()
            if not school:
                return Response({"error": "school not Found"}, status=status.HTTP_200_OK)
            school_identities = school.biometric_identities.all()[:50]
            serializer = BiometricIdentitySerializer(school_identities, many=True, context={"request": request})
            return Response({"success":"Biometric Datas","allBioData":serializer.data}, status=status.HTTP_201_CREATED)
        except:
            return Response({"error":"server error"},status=status.HTTP_200_OK) 
        
    def post(self, request, school_id) :
        try:
            director = request.user.director
             # validate director actions  on his school only
            school = School.objects.filter(director_id = director.id, id=school_id).first()  #.exists()
            if not school:
                return Response({"error": "school not Found"}, status=status.HTTP_200_OK)
            # Assuming faceData is sent as a list of image paths or base64 strings
            frames = json.loads(request.data.get("faceData", "[]"))
            if not isinstance(frames, list):
                return Response({"error": "faceData must be a list"}, status=status.HTTP_200_OK)
            user = None 
            userId = request.data.get("userId")
            userType = request.data.get("userType")
            if userType == "student" :
                user = school.students.filter(user__id = userId).first()
            
            elif userType == "teacher" :
                user = school.teachers.filter(user__id = userId).first()
                
            elif userType == "staff" :
                user = school.staffs.filter(user__id = userId).first()
                
            elif userType == "director" :
                if school.director.user.id == userId :
                    user = school.director.user
            
            if user is None :
                return Response({"error": "user not found!"}, status=status.HTTP_200_OK)
            
            serializer = BiometricIdentitySerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                biometric = serializer.save()
                data =  BiometricIdentitySerializer(biometric).data 
                return Response({"success":"Biometric Data Created","createdBioData":data}, status=status.HTTP_201_CREATED)

            return Response({"error":serializer.errors},status=status.HTTP_200_OK) 
        except:
            return Response({"error":"server error"},status=status.HTTP_200_OK) 
        
    def delete(self, request, school_id,biometric_id,pin) :
        try:
            director = request.user.director
             # validate director actions  on his school only
            school = School.objects.filter(director_id = director.id, id=school_id).first()  #.exists()
            if not school:
                return Response({"error": "school not Found"}, status=status.HTTP_200_OK)
            
            # validate pin 
            if not request.user.pins.checkPin(pin) :
                return Response({"error" : "Incorrect PIN"}, status=status.HTTP_200_OK)
            
            # validate biometric 
            valid_identity = BiometricIdentity.objects.filter(id = biometric_id).first()
            if not valid_identity :
                    return Response({"error": "Identity not found "}, status=status.HTTP_200_OK)
                
            valid_identity.delete()
            data = {"id":biometric_id,}
            return Response({"success":"Biometric Data Deleted","deletedBioData":data}, status=status.HTTP_201_CREATED)
        except:
            return Response({"error":"server error"},status=status.HTTP_200_OK) 
        
    def put(self, request, school_id,biometric_id) :
        try:
            director = request.user.director
             # validate director actions  on his school only
            school = School.objects.filter(director_id = director.id, id=school_id).first()  #.exists()
            if not school:
                return Response({"error": "school not Found"}, status=status.HTTP_200_OK)
            
            # validate pin 
            pin = request.data.get('pin')
            if not request.user.pins.checkPin(pin) :
                return Response({"error" : "Incorrect PIN"}, status=status.HTTP_200_OK)
            
            # validate biometric 
            valid_identity = school.biometric_identities.filter(id = biometric_id).first()
            if not valid_identity :
                    return Response({"error": "Identity not found "}, status=status.HTTP_200_OK)
            
            serializer = UpdateBiometricIdentitySerializer(valid_identity,data=request.data, context={"request": request})
            if serializer.is_valid():
                biometric = serializer.save()
                data = BiometricIdentitySerializer(biometric).data
                return Response({"success":"Biometric Data Updated","updatedBioData":data}, status=status.HTTP_200_OK)

            return Response({"error":serializer.errors},status=status.HTTP_200_OK) 
        except:
            return Response({"error":"server error"},status=status.HTTP_200_OK) 
        
class DeviceView(APIView) :
    # parser_classes =[MultiPartParser,FormParser]
    permission_classes=[
        permissions.IsAuthenticated,
        DirectorUserPermission,
    ]
    
    def get(self, request, school_id) : # get all  limited to 50 biometric identities for the school in firts call
        try:
            director = request.user.director
             # validate director actions  on his school only
            school = School.objects.filter(director_id = director.id, id=school_id).first()  #.exists()
            if not school:
                return Response({"error": "school not Found"}, status=status.HTTP_200_OK)
            school_identities = school.devices.all()[:50]
            serializer = DeviceSerializer(school_identities, many=True, context={"request": request})
            return Response({"success":"Device Datas","allDeviceData":serializer.data}, status=status.HTTP_201_CREATED)
        except:
            return Response({"error":"server error"},status=status.HTTP_200_OK) 
        
    def post(self, request, school_id) :
        # try:
            director = request.user.director
             # validate director actions  on his school only
            school = School.objects.filter(director_id = director.id, id=school_id).first()  #.exists()
            if not school:
                return Response({"error": "school not Found"}, status=status.HTTP_200_OK)
             # validate pin 
            pin = request.data.get('pin')
            if not request.user.pins.checkPin(pin) :
                return Response({"error" : "Incorrect PIN"}, status=status.HTTP_200_OK)
            name = request.data.get("name")
            if school.devices.filter(name = name).exists() :
                return Response({"error": "Device with this name already exists"}, status=status.HTTP_200_OK)
            
            serializer = DeviceSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                device = serializer.save()
                data =  DeviceSerializer(device).data 
                return Response({"success":"Device Data Created","createdDeviceData":data}, status=status.HTTP_201_CREATED)

            return Response({"error":serializer.errors},status=status.HTTP_200_OK) 
        # except:
            # return Response({"error":"server error"},status=status.HTTP_200_OK) 
        
    def delete(self, request, school_id,device_id,pin) :
        try:
            director = request.user.director
             # validate director actions  on his school only
            school = School.objects.filter(director_id = director.id, id=school_id).first()  #.exists()
            if not school:
                return Response({"error": "school not Found"}, status=status.HTTP_200_OK)
            
            # validate pin 
            if not request.user.pins.checkPin(pin) :
                return Response({"error" : "Incorrect PIN"}, status=status.HTTP_200_OK)
            
            # validate biometric 
            valid_identity = school.devices.filter(id = device_id).first()
            if not valid_identity :
                    return Response({"error": "Device not found "}, status=status.HTTP_200_OK)
                
            valid_identity.delete()
            data = {"id":device_id,'name':valid_identity.name}
            return Response({"success":"Device Data Deleted","deletedDeviceData":data}, status=status.HTTP_201_CREATED)
        except:
            return Response({"error":"server error"},status=status.HTTP_200_OK) 
        
    def put(self, request, school_id,device_id) :
        try:
            director = request.user.director
             # validate director actions  on his school only
            school = School.objects.filter(director_id = director.id, id=school_id).first()  #.exists()
            if not school:
                return Response({"error": "school not Found"}, status=status.HTTP_200_OK)
            
            # validate pin 
            pin = request.data.get('pin')
            if not request.user.pins.checkPin(pin) :
                return Response({"error" : "Incorrect PIN"}, status=status.HTTP_200_OK)
            # valide name not exist in one school 
            
            name = request.data.get("name")
            valid_identity = school.devices.filter(id = device_id).first()
            nameExist = school.devices.filter(name = name).exclude(id=device_id).exists()

            if  not name == valid_identity.name and nameExist :
                return Response({"error": "Device with this name already exists!"}, status=status.HTTP_200_OK)
            # validate device 
            if not valid_identity :
                    return Response({"error": "Device not found "}, status=status.HTTP_200_OK)
            
            serializer = DeviceSerializer(valid_identity,data=request.data, context={"request": request})
            if serializer.is_valid():
                device = serializer.save()
                data = DeviceSerializer(device).data
                return Response({"success":"Device Data Updated","updatedDeviceData":data}, status=status.HTTP_200_OK)

            return Response({"error":serializer.errors},status=status.HTTP_200_OK) 
        except:
            return Response({"error":"server error"},status=status.HTTP_200_OK) 
        
