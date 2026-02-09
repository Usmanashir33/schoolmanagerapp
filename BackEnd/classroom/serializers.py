from rest_framework import serializers
from .models import ClassRoom
from teacher.serializers import TeacherSerializer

class ClassRoomDetailSerializer(serializers.ModelSerializer) :
    class Meta:  
        model = ClassRoom 
        fields ='__all__'
        read_only_fields = ['id', 'joined_at']
        
        
