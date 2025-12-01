from rest_framework import serializers
from .models import School, Student, Teacher, SchoolSection, ClassRoom, Parents, Subject

from authUser.serializers import MiniUserSerializer
class SchoolSerializer(serializers.ModelSerializer):
    director = MiniUserSerializer(read_only=True)
    class Meta:  
        model = School
        fields ='__all__'
        read_only_fields = ['id', 'joined_at']
        
class SchoolSectionSerializer(serializers.ModelSerializer):
    school = SchoolSerializer(read_only=True)
    class Meta:  
        model = SchoolSection 
        fields ='__all__'
        read_only_fields = ['id', 'joined_at']
        
# creat teacher serializers
class TeacherSerializer(serializers.ModelSerializer): 
    user = MiniUserSerializer(read_only=True)
    school = SchoolSerializer()
    section = SchoolSectionSerializer()   
    class Meta:  
        model = Teacher 
        fields ='__all__'
        read_only_fields = ['id', 'joined_at']
class ClassRoomSerializer(serializers.ModelSerializer) :
    section  = SchoolSectionSerializer(read_only=True)
    class_teacher = TeacherSerializer()
    class Meta:  
        model = Teacher 
        fields ='__all__'
        read_only_fields = ['id', 'joined_at']
        
# serializers.py
from rest_framework import serializers
from .models import Student

class StudentSerializer(serializers.ModelSerializer):
    class_room = ClassRoomSerializer(read_only = True)
    class Meta:
        model = Student
        fields = '__all__'

