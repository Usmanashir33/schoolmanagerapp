from rest_framework import serializers

from subject .models import Subject
from classroom.models import ClassRoom
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
        read_only_fields = ['id', 'added_at','class_rooms','teacher']
        
    def create(self, validated_data) :
        request = self.context["request"]
        class_rooms = request.data.get("class_room_ids", [])
        with transaction.atomic():
            subject = Subject.objects.create(**validated_data)
            if class_rooms:
                subject.class_rooms.set(ClassRoom.objects.filter(id__in = class_rooms))
            subject.save()
        return subject 
    
    # handle enroll into classes 
    def update(self, instance, validated_data):
        request = self.context["request"]
        class_room_ids = request.data.get("class_room_ids", None)
        # print('class_room_ids: ', class_room_ids)
        teachers_ids = request.data.get("teachers", None)
        
         # ✅ FIX: safe JSON parsing
        
        with transaction.atomic():
            # update subject 
            for field ,value in validated_data.items() :
                setattr(instance,field,value)
            
            if class_room_ids is not None:
                instance.class_rooms.set (
                    ClassRoom.objects.filter(id__in = class_room_ids)
                ) 
            if teachers_ids is not None:
                instance.teacher.set (
                    Teacher.objects.filter(id__in=teachers_ids)
                ) 
                
            instance.save()
                
        return instance 
