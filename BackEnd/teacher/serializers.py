from rest_framework import serializers
from .models import Teacher
from authUser.serializers import MiniUserSerializer


class TeacherSerializer(serializers.ModelSerializer): 
    user = MiniUserSerializer(read_only=True)
    class Meta:  
        model = Teacher 
        fields ='__all__'
        read_only_fields = ['id', 'joined_at']