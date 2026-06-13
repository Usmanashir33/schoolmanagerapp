from rest_framework import serializers

from school.models import School,SchoolDeleteRequest
from school.serializers import TermSerializer, SessionSerializer
from academics.serializers import MiniClassRoomSerializer,MiniSchoolSectionSerializer,SubjectSerializer
from student.models import Student,StudentClassEnrollment
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
        
 
class SchoolDeleteRequestSerialzer(serializers.ModelSerializer):
    # classrooms = MiniClassRoomSerializer(many=True, read_only=True)
    class Meta:  
        model = SchoolDeleteRequest
        fields ='__all__'
        read_only_fields = ['id', 'requested_at']  

class DirectorSchoolSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField(read_only =True)
    sections = MiniSchoolSectionSerializer(many=True, read_only=True) # sections full 
    classrooms =   MiniClassRoomSerializer(many=True, read_only =  True) # classroom full data
    subjects = SubjectSerializer(many=True, read_only =  True)
    
    terms = TermSerializer(read_only=True,many=True)
    sessions = SessionSerializer(read_only=True,many=True)
    delete_requests = SchoolDeleteRequestSerialzer(read_only = True)
    
    total_teachers = serializers.SerializerMethodField(read_only = True)
    total_students = serializers.SerializerMethodField(read_only = True)
    total_staffs = serializers.SerializerMethodField(read_only = True)
    
    total_classrooms = serializers.SerializerMethodField(read_only = True)
    total_sections = serializers.SerializerMethodField(read_only = True)
    total_subjects = serializers.SerializerMethodField(read_only = True)
    class Meta:  
        model = School
        fields ='__all__'
        read_only_fields = ['id', 'joined_at','ref_id','director']
    
    def get_total_teachers(self,obj) :
        all = {"count":obj.teachers.count(),
            "active":obj.teachers.filter(user__is_active = True).count(),
            "inactive":obj.teachers.filter(user__is_active = False).count()
            }
        return all
    
    def get_total_students(self,obj) :
        all = {"count":obj.students.count(),
            "active":obj.students.filter(user__is_active = True).count(),
            "inactive":obj.students.exclude(user__is_active = True).count() # because student can exist with out user
            }
        return all 
    
    def get_total_staffs(self,obj) :
        all = {"count":obj.staffs.count(),
            "active":obj.staffs.filter(user__is_active = True).count(),
            "inactive":obj.staffs.filter(user__is_active = False).count()
            }
        return all
    
    def get_total_classrooms(self,obj) :
        return obj.classrooms.count()
    
    def get_total_sections(self,obj) :
        return obj.sections.count()
    
    def get_total_subjects(self,obj) :
        return obj.subjects.count()
    
    def get_logo(self, obj):
        return obj.logo.url if obj.logo else None
    
        
    
    
# --------------Director Role ------------------
class DirectorSerializer(serializers.ModelSerializer): 
    picture = serializers.SerializerMethodField()
    user = MiniUserSerializer(read_only=True)
    directorschools = DirectorSchoolSerializer(many=True, read_only=True)
    def get_picture(self, obj):

        return obj.picture.url if obj.picture else None
    class Meta:  
        model = Director 
        fields ='__all__'
        read_only_fields = ['id', 'joined_at']

# --------- Teacher Role  ------------------  
class TeacherSerializer(serializers.ModelSerializer): 
    user = MiniUserSerializer(read_only=True)
    # school = SchoolSerializer()
    class Meta:  
        model = Teacher 
        fields ='__all__'
        read_only_fields = ['id', 'joined_at']
    

class StaffSerializer(serializers.ModelSerializer):
    # school = SchoolSerializer()
    user = MiniUserSerializer(read_only=True)
    class Meta:
        model = Staff
        fields = '__all__'
        read_only_fields = ['id', 'joined_at']
        
        
class StudentSerializer(serializers.ModelSerializer):
    # school = SchoolSerializer()
    user = MiniUserSerializer(read_only=True)
    class Meta:
        model = Student
        fields = '__all__' 

class ParentsSerializer(serializers.ModelSerializer):
    user = MiniUserSerializer(read_only=True)
    # schools = SchoolSerializer(many=True, read_only=True)
    students = StudentSerializer(read_only=True)
    class Meta:
        model = Parents
        fields = '__all__'
        read_only_fields = ['id', 'joined_at']                      
                  