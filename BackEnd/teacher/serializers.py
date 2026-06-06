from rest_framework import serializers
from .models import Teacher 
from authUser.serializers import MiniUserSerializer
from django.db import transaction
from .models import Teacher
from core.models import BankDetails
import json
from .models import DisplinaryRecord
from school.models import ActivityLog
from school.serializers import ActivityLogSerializer
from school.tasks import SchoolServices
class BankSerializer(serializers.ModelSerializer) : 
    class Meta:  
        model = BankDetails 
        fields ='__all__'
        read_only_fields = ['id', 'created_at']
        
class DisplinaryRecordSerializer(serializers.ModelSerializer ) :
    class Meta:
        model = DisplinaryRecord
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
        
class TeacherSerializer(serializers.ModelSerializer):  #initial fatch
    picture = serializers.SerializerMethodField(read_only=True)
    is_active = serializers.SerializerMethodField(read_only=True)
    class_rooms = serializers.SerializerMethodField(read_only=True)
    
    def get_picture(self, obj):
        return obj.picture.url if obj.picture else None
    
    def get_is_active(self, obj):
        return obj.user.is_active
    
    def get_class_rooms(self, obj):
        return list(
           obj.teaching_assignments.values_list("classroom__id", flat=True)
        )
    class Meta:
        model = Teacher
        fields = ['id',"staff_id",'first_name',"last_name",'middle_name','title','joined_at','picture','is_active','email','phone','class_rooms']
        read_only_fields = ['id',"staff_id",'first_name',"last_name",'middle_name','email','picture']

 
        
class MiniTeacherSerializer(serializers.ModelSerializer): # teachers list 
    picture = serializers.SerializerMethodField(read_only=True)
    is_active = serializers.SerializerMethodField(read_only=True)
    
    def get_picture(self, obj):
        return obj.picture.url if obj.picture else None
    
    def get_is_active(self, obj):
        return obj.user.is_active
    class Meta:
        model = Teacher
        fields = ['id',"staff_id",'first_name',"last_name",'middle_name','title','picture','is_active','email','phone']
        read_only_fields = ['id',"staff_id",'first_name',"last_name",'middle_name','email','picture']

 

class TeacherDetailSerializer(serializers.ModelSerializer) :
    picture = serializers.SerializerMethodField()
    # user = MiniUserSerializer(read_only = True)
    bank_details = BankSerializer(read_only = True )
    disciplinaryRecords = DisplinaryRecordSerializer(read_only=True,many=True,)
    is_active = serializers.SerializerMethodField(read_only=True)
    class_rooms = serializers.SerializerMethodField(read_only=True)
    form_classes = serializers.SerializerMethodField(read_only=True)
    sections = serializers.SerializerMethodField(read_only=True)
    subjects = serializers.SerializerMethodField(read_only=True)
    
    
    class Meta:
        model = Teacher
        fields = "__all__"
        read_only_fields = ["id", "staff_id", "joined_at", "user","class_room"]
    def get_sections(self, obj):
        return list(
           obj.teaching_assignments.values_list("classroom__section__id", flat=True)
        )
    def get_class_rooms(self, obj):
        return list(
           obj.teaching_assignments.values_list("classroom__id", flat=True)
        )
    def get_form_classes(self, obj):
        return list(
           obj.form_classes.values_list("id", flat=True)
        )
    def get_subjects(self, obj):
        return list(
           obj.teaching_assignments.values("subject__name","subject__code",'classroom__name','id')
        )
        
    def get_is_active(self, obj):
        return obj.user.is_active
    
    def get_picture(self, obj):
        if obj.picture:
            return obj.picture.url
        return None
class TeacherCreateSerializer(serializers.ModelSerializer):
    picture = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = "__all__"
        read_only_fields = ["id", "staff_id", "joined_at", "user",'bank_details']

    
    def get_picture(self, obj):
        if obj.picture:
            return obj.picture.url
        return None


    def create(self, validated_data):
        request = self.context["request"]
        bank_details_data = request.data.get("bank_details", [])
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
            if bank.is_valid():
                bank.save()
                teacher.bank_details = bank.instance
                
            if picture_file :
                teacher.picture = picture_file
            
            teacher.save()
                
        return teacher 
    
    def update(self, instance, validated_data):
        request = self.context["request"]
        bank_details_data = request.data.get("bank_details", [])
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
                
            if picture_file:
                instance.picture = picture_file
            instance.save()
             # configuring activity log data 
             
            new_log = ActivityLog.objects.create(
                    school = instance.school,
                    user=request.user,
                    action="UPDATE",
                    module="TEACHER",
                    description=f"{instance.staff_id} • {instance.full_name()}"
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
