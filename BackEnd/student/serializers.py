from rest_framework import serializers
from .models import  Student
from core.serializers import  ClassRoomSerializer
from authUser.serializers import MiniUserSerializer

class StudentSerializer(serializers.ModelSerializer):
    class_room = ClassRoomSerializer(read_only=True,many=True)
    user = MiniUserSerializer(read_only=True)
    class Meta:
        model = Student
        fields = '__all__'
class MiniStudentSerializer(serializers.ModelSerializer):
    user = MiniUserSerializer(read_only=True)
    class Meta:
        model = Student 
        fields = '__all__'

