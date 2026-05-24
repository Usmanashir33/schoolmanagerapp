from rest_framework import serializers

from school.models import School,SchoolDeleteRequest
from school.serializers import TermSerializer, SessionSerializer
from academics.models import SchoolSection,Subject,ClassRoom
from student.models import Student
from teacher.models import Teacher
from director.models import Director
from parent.models import Parents 
from staff.models import Staff
from core .models import BankDetails 
from authUser.serializers import MiniUserSerializer

class BankSerializer(serializers.ModelSerializer) : 
    class Meta:  
        model = BankDetails 
        fields ='__all__'
        read_only_fields = ['id', 'created_at']
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
class SchoolDeleteRequestSerialzer(serializers.ModelSerializer):
    classrooms = ClassRoomSerializer(many=True, read_only=True)
    class Meta:  
        model = SchoolDeleteRequest
        fields ='__all__'
        read_only_fields = ['id', 'requested_at']  

class SchoolSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField(read_only =True)
    sections = SchoolSectionSerializer(many=True, read_only=True) # sections full and classroom full data
    terms = TermSerializer(read_only=True,many=True)
    sessions = SessionSerializer(read_only=True,many=True)
    delete_requests = SchoolDeleteRequestSerialzer(read_only = True)
    
    total_teachers = serializers.SerializerMethodField(read_only = True)
    total_students = serializers.SerializerMethodField(read_only = True)
    total_staffs = serializers.SerializerMethodField(read_only = True)
    total_classrooms = serializers.SerializerMethodField(read_only = True)
    total_parents = serializers.SerializerMethodField(read_only = True) 
    total_sections = serializers.SerializerMethodField(read_only = True)
    class Meta:  
        model = School
        fields ='__all__'
        read_only_fields = ['id', 'joined_at','ref_id','director']
        
    def get_logo(self, obj):
        return obj.logo.url if obj.logo else None
    
    def get_total_teachers(self, obj):
        return obj.teachers.all().count()
    
    def get_total_students(self, obj):
        return obj.students.all().count()
    
    def get_total_staffs(self, obj):
        return obj.staffs.all().count()  
    
    def get_total_parents(self, obj):
        return obj.parents.all().count()
    
    def get_total_sections(self, obj):
        return obj.sections.all().count()
    
    def get_total_classrooms(self, obj):
        total_classrooms = ClassRoom.objects.filter(section__school=obj).count()
        return total_classrooms
    
    def update(self, instance, validated_data):
        request = self.context['request']
        logo = request.FILES.get("logo")
        

        # update only provided fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        if logo :
            instance.logo = logo

        # save updated instance
        instance.save()

        return instance
        
    
    
# --------------Director Role ------------------
class DirectorSerializer(serializers.ModelSerializer): 
    picture = serializers.SerializerMethodField()
    user = MiniUserSerializer(read_only=True)
    directorschools = SchoolSerializer(many=True, read_only=True)
    def get_picture(self, obj):

        return obj.picture.url if obj.picture else None
    class Meta:  
        model = Director 
        fields ='__all__'
        read_only_fields = ['id', 'joined_at']

# --------- Teacher Role  ------------------  
class TeacherSerializer(serializers.ModelSerializer): 
    user = MiniUserSerializer(read_only=True)
    school = SchoolSerializer()
    # section = SchoolSectionSerializer()   
    class Meta:  
        model = Teacher 
        fields ='__all__'
        read_only_fields = ['id', 'joined_at']
    

class StaffSerializer(serializers.ModelSerializer):
    school = SchoolSerializer()
    user = MiniUserSerializer(read_only=True)
    class Meta:
        model = Staff
        fields = '__all__'
        read_only_fields = ['id', 'joined_at']
        
        
class StudentSerializer(serializers.ModelSerializer):
    school = SchoolSerializer()
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
                  