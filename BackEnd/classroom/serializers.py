from rest_framework import serializers
from .models import ClassRoom ,PromotionLog
from teacher.serializers import TeacherSerializer

class ClassRoomDetailSerializer(serializers.ModelSerializer) :
    class Meta:  
        model = ClassRoom 
        fields ='__all__'
        read_only_fields = ['id', 'joined_at']

class PromotionLogSerializer(serializers.ModelSerializer) :
    class Meta:  
        model = PromotionLog
        fields ='__all__'
        read_only_fields = ['id', 'created_at']
        
        
