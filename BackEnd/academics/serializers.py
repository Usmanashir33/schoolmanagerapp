from rest_framework import serializers
from .models import SchoolSection

#------------------------------------------------------------------------------------
#                                    SECTION SERIALIZERS
#------------------------------------------------------------------------------------
class SchoolSectionSerializer(serializers.ModelSerializer):
    # school = SchoolSerializer(read_only=True)
    class Meta:  
        model = SchoolSection 
        fields ='__all__'
        read_only_fields = ['id', 'joined_at']
        
class SchoolSectionCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:  
        model = SchoolSection 
        fields ='__all__'
        read_only_fields = ['id', 'joined_at']
        
class SchoolSectionDetailSerializer(serializers.ModelSerializer):
    class Meta:  
        model = SchoolSection 
        fields ='__all__'
        read_only_fields = ['id', 'joined_at']
        
        
        

#--------------------------------------------------------------------------------------
#                                    CLASSROOM SERIALIZERS

from .models import ClassRoom ,PromotionLog
from teacher.serializers import TeacherSerializer

class ClassRoomDetailSerializer(serializers.ModelSerializer) :
    class Meta:  
        model = ClassRoom 
        fields ='__all__'
        read_only_fields = ['id', 'joined_at']
class ClassRoomCreateUpdateSerializer(serializers.ModelSerializer) :
    class Meta:  
        model = ClassRoom 
        fields ='__all__'
        read_only_fields = ['id', 'joined_at']

class PromotionLogSerializer(serializers.ModelSerializer) :
    class Meta:  
        model = PromotionLog
        fields ='__all__'
        read_only_fields = ['id', 'created_at']
        
        
        
        
#------------------------------------------------------------------------------------------------
#                           SUBJECT SERIALIZERS
#------------------------------------------------------------------------------------------------
from .models import Subject,ClassRoom
from teacher.models import Teacher
from django.db import transaction

    
class SubjectSerializer(serializers.ModelSerializer) :
    class Meta:  
        model = Subject   
        fields ='__all__' 
        read_only_fields = ['id', 'added_at']
    
class SubjectDetailSerializer(serializers.ModelSerializer) :
    class Meta:  
        model = Subject 
        fields ='__all__' 
        read_only_fields = ['id', 'added_at','class_rooms','teachers']
        
class SubjectCreateUpdateSerializer(serializers.ModelSerializer) :
    class Meta:  
        model = Subject 
        fields ='__all__' 
        read_only_fields = ['id', 'added_at','class_rooms','teachers']
        
    def create(self, validated_data) :
        request = self.context["request"]
        school_id = self.context["school_id"]
        class_rooms_ids = request.data.get("class_room_ids", [])
        class_rooms = ClassRoom.objects.filter(section__school__id = school_id, id__in = class_rooms_ids)
        
        with transaction.atomic():
            subject = Subject.objects.create(**validated_data)
            if class_rooms:
                subject.class_rooms.set(class_rooms)
            subject.save()
        return subject 
    
    def update(self, instance, validated_data):
        request = self.context["request"]
        school_id = self.context["school_id"]
        
        class_room_ids = request.data.get("class_room_ids", [])
        teachers_ids = request.data.get("teachers", [])
        
        class_rooms = ClassRoom.objects.filter(section__school__id = school_id, id__in = class_room_ids)
        
        with transaction.atomic():
            # update subject 
            for field ,value in validated_data.items() :
                setattr(instance,field,value)
            
            if class_rooms.exists()  :
                instance.class_rooms.set(class_rooms) 
                
            if teachers_ids is not None:
                instance.teachers.set (
                    Teacher.objects.filter(id__in=teachers_ids,school_id =school_id)
                ) 
                
            instance.save()
                
        return instance 
