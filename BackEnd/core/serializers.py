from rest_framework import serializers

from school.models import School
from section.models import SchoolSection
from student.models import Student
from teacher.models import Teacher
from classroom.models import ClassRoom
from director.models import Director
from parent.models import Parents 
from staff.models import Staff
from authUser.serializers import MiniUserSerializer
    
class ClassRoomSerializer(serializers.ModelSerializer) :
    class Meta:  
        model = ClassRoom 
        fields ='__all__'
        read_only_fields = ['id', 'joined_at']
        
class SchoolSectionSerializer(serializers.ModelSerializer):
    classrooms = ClassRoomSerializer(many=True, read_only=True)
    class Meta:  
        model = SchoolSection 
        fields ='__all__'
        read_only_fields = ['id', 'joined_at']
        
class SchoolSerializer(serializers.ModelSerializer):
    sections = SchoolSectionSerializer(many=True, read_only=True)
    class Meta:  
        model = School
        fields ='__all__'
        read_only_fields = ['id', 'joined_at']
        
        
# --------------Director Role ------------------
class DirectorSerializer(serializers.ModelSerializer):
    user = MiniUserSerializer(read_only=True)
    directorschools = SchoolSerializer(many=True, read_only=True)
    class Meta:  
        model = Director 
        fields ='__all__'
        read_only_fields = ['id', 'joined_at']

# --------- Teacher Role  ------------------  
class TeacherSerializer(serializers.ModelSerializer): 
    user = MiniUserSerializer(read_only=True)
    # school = SchoolSerializer()
    # section = SchoolSectionSerializer()   
    class Meta:  
        model = Teacher 
        fields ='__all__'
        read_only_fields = ['id', 'joined_at']
     
    

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = '__all__'
        read_only_fields = ['id', 'joined_at']
        
        
class StudentSerializer(serializers.ModelSerializer):
    # class_room = ClassRoomSerializer(read_only = True)
    user = MiniUserSerializer(read_only=True)
    class Meta:
        model = Student
        fields = '__all__'

class ParentsSerializer(serializers.ModelSerializer):
    user = MiniUserSerializer(read_only=True)
    schools = SchoolSerializer(many=True, read_only=True)
    students = StudentSerializer(read_only=True)
    
    class Meta:
        model = Parents
        fields = '__all__'
        read_only_fields = ['id', 'joined_at']                      
                  