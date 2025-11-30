from rest_framework import serializers
from .models import School, Student, Teacher, SchoolSection, ClassRoom, Parents, Subject

from authUser.serializers import MiniUserSerializer
class SchoolSerializer(serializers.ModelSerializer):
    director = MiniUserSerializer(read_only=True)   
    
    class Meta:  
        model = School
        fields ='__all__'
        read_only_fields = ['id', 'joined_at',]
