from rest_framework import serializers
from .models import Teacher

# class SchoolSerializer(serializers.ModelSerializer):
#     director = DirectorSerializer(read_only=True)
#     class Meta:  
#         model = School
#         fields ='__all__'
#         read_only_fields = ['id', 'joined_at']
        
# class SchoolSectionSerializer(serializers.ModelSerializer):
#     school = SchoolSerializer(read_only=True)
#     class Meta:  
#         model = SchoolSection 
#         fields ='__all__'
#         read_only_fields = ['id', 'joined_at']
        
# creat teacher serializers
class TeacherSerializer(serializers.ModelSerializer): 
    # user = MiniUserSerializer(read_only=True)
    # school = SchoolSerializer()
    # section = SchoolSectionSerializer()   
    class Meta:  
        model = Teacher 
        fields ='__all__'
        read_only_fields = ['id', 'joined_at']