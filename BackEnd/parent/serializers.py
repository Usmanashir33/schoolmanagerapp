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
    
class MiniParentsSerializer(serializers.ModelSerializer):
    user = MiniUserSerializer(read_only=True)
    class Meta:
        model = Parents
        fields = '__all__'
        read_only_fields = ['id', 'joined_at']                      
                  
