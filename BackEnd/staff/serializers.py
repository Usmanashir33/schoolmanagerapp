 
from rest_framework import serializers
from staff.models import Staff , ActivityRole
from core.serializers import BankSerializer 
from authUser.serializers import MiniUserSerializer
import json 
from django.db import transaction


class ActivityRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityRole
        fields = '__all__' 
class StaffSerializer(serializers.ModelSerializer):
    user = MiniUserSerializer(read_only=True)
    class Meta:
        model = Staff
        fields = '__all__' 
        
class StaffDetailSerializer(serializers.ModelSerializer):
    picture        = serializers.SerializerMethodField()
    user           = MiniUserSerializer(read_only=True)
    bank_details   = BankSerializer(read_only=True)
    activity_role  = ActivityRoleSerializer(read_only=True)
    class Meta:
        model = Staff
        fields = '__all__'
        
    def get_picture(self, obj):
        if obj.picture:
            return obj.picture.url
        return None

    def create(self, validated_data):
        request = self.context["request"]
        bank_details_data = request.data.get("bank_details", [])
        activity_role = request.data.get("activity_role")
        picture_file = request.FILES.get("picture")
        
        # ✅ FIX: safe JSON parsing
        if bank_details_data:
            try:
                bank_data = json.loads(bank_details_data)
            except (TypeError, ValueError):
                bank_details_data = None
                
        # ✅ FIX: safe JSON parsing
        if activity_role:
            try:
                activity_role = json.loads(activity_role)
            except (TypeError, ValueError):
                activity_role = None
        
        with transaction.atomic():
            staff = Staff.objects.create(**validated_data)
            bank = BankSerializer(data = bank_data)
            if bank.is_valid() :
                bank.save()
                staff.bank_details = bank.instance
                
            activity_role = ActivityRoleSerializer(data = activity_role)
            if activity_role.is_valid() :
                activity_role.save()
                staff.activity_role = activity_role.instance

            if picture_file:
                staff.picture = picture_file
            
            staff.save()
                
        return staff 
    
    def update(self, instance, validated_data):
        request = self.context["request"]
        bank_details_data = request.data.get("bank_details", [])
        activity_role = request.data.get("activity_role")
        picture_file = request.FILES.get("picture")
        
        # ✅ FIX: safe JSON parsing
        if bank_details_data:
            try:
                bank_data = json.loads(bank_details_data)
            except (TypeError, ValueError):
                bank_details_data = None
                
        # ✅ FIX: safe JSON parsing
        if activity_role:
            try:
                activity_role = json.loads(activity_role)
            except (TypeError, ValueError):
                activity_role = None
        
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
                
            # handle actiity role 
            role = instance.activity_role
            if not role : #create 
                activity_role = ActivityRoleSerializer(data = activity_role)
            else : # Update 
                activity_role = ActivityRoleSerializer(role, data=activity_role, partial=True )
            if activity_role.is_valid() :
                activity_role.save()
                instance.activity_role = activity_role.instance
            if picture_file:
                instance.picture = picture_file
            instance.save()
                
        return instance 
