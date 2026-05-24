from rest_framework import serializers
from .models import Teacher 
from authUser.serializers import MiniUserSerializer
from django.db import transaction
from .models import Teacher
from core.models import BankDetails
from academics.models import ClassRoom,SchoolSection
from core.serializers import ClassRoomSerializer,BankSerializer
import json
from .models import DisplinaryRecord
from school.models import ActivityLog
from school.serializers import ActivityLogSerializer
from school.tasks import SchoolServices

class DisplinaryRecordSerializer(serializers.ModelSerializer ) :
    class Meta:
        model = DisplinaryRecord
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
        
class DisplinaryRecordIDSerializer(serializers.ModelSerializer ) :
    class Meta:
        model = DisplinaryRecord
        fields = ['id',]
        
class TeacherSerializer(serializers.ModelSerializer): 
    user = MiniUserSerializer(read_only=True)
    bank_details = BankSerializer(read_only = True )
    disciplinaryRecords = DisplinaryRecordSerializer(read_only=True,many=True,)
    
    class Meta:  
        model = Teacher 
        fields ='__all__'
        read_only_fields = ['id', 'joined_at']
class MiniTeacherSerializer(serializers.ModelSerializer):  # for websocket 
    user = MiniUserSerializer(read_only=True)
    class Meta:  
        model = Teacher 
        fields ='__all__'
        read_only_fields = ['id',]
 

class TeacherDetailSerializer(serializers.ModelSerializer):
    picture = serializers.SerializerMethodField()
    user = MiniUserSerializer(read_only = True)
    bank_details = BankSerializer(read_only = True )
    disciplinaryRecords = DisplinaryRecordIDSerializer(read_only=True,many=True,)
    
    class Meta:
        model = Teacher
        fields = "__all__"
        read_only_fields = ["id", "staff_id", "joined_at", "user","class_room"]

    
    def get_picture(self, obj):
        if obj.picture:
            return obj.picture.url
        return None
class TeacherCreateSerializer(serializers.ModelSerializer):
    picture = serializers.SerializerMethodField()
    user = MiniUserSerializer(read_only = True)
    bank_details = BankSerializer(read_only = True )

    class Meta:
        model = Teacher
        fields = "__all__"
        read_only_fields = ["id", "staff_id", "joined_at", "user","class_room"]

    
    def get_picture(self, obj):
        if obj.picture:
            return obj.picture.url
        return None


    def create(self, validated_data):
        request = self.context["request"]
        bank_details_data = request.data.get("bank_details", [])
        class_rooms = request.data.getlist("class_rooms", [])
        picture_file = request.FILES.get("picture")
        
        # ✅ FIX: safe JSON parsing
        if bank_details_data:
            try:
                bank_data = json.loads(bank_details_data)
            except (TypeError, ValueError):
                bank_details_data = None
        
        with transaction.atomic():
            teacher = Teacher.objects.create(**validated_data)
            bank = BankSerializer(data = bank_data)
            if bank.is_valid() :
                bank.save()
                teacher.bank_details = bank.instance

            if class_rooms:
                teacher.class_room.set(ClassRoom.objects.filter(id__in = class_rooms))
                
            if picture_file:
                teacher.picture = picture_file
            
            teacher.save()
                
        return teacher 
    
    def update(self, instance, validated_data):
        request = self.context["request"]
        bank_details_data = request.data.get("bank_details", [])
        class_room_ids = request.data.getlist("class_rooms", [])
        picture_file = request.FILES.get("picture")
        
         # ✅ FIX: safe JSON parsing
        if bank_details_data:
            try:
                bank_data = json.loads(bank_details_data)
            except (TypeError, ValueError):
                bank_data = None
        
        with transaction.atomic():
            # update teacher 
            for field ,value in validated_data.items() :
                setattr(instance,field,value)
                
            bank = instance.bank_details
            if not bank : #create 
                bank = BankSerializer(data =bank_data)
            else : # Update 
                bank = BankSerializer(bank , data =bank_data,partial=True )
            
            if bank.is_valid() :
                bank.save()
                instance.bank_details = bank.instance
            if class_room_ids:
                instance.class_room.set(
                    ClassRoom.objects.filter(id__in=class_room_ids)
                )
                
            if picture_file:
                instance.picture = picture_file
            instance.save()
             # configuring activity log data 
             
            new_log = ActivityLog.objects.create(
                    school = instance.school,
                    user=request.user,
                    action="UPDATE",
                    module="TEACHER",
                    description=f"Teacher updated: {instance.staff_id} - {instance.full_name()}"
                )
            user_room = f"room{request.user.id}"
            log_data = ActivityLogSerializer(new_log).data
            data = {
                    "type": "send_response1",
                    "activity_log": log_data,
                    }
            try:
                SchoolServices.send_activity_log.delay(destination=user_room, data=data)
            except :
                pass
                
        return instance 
