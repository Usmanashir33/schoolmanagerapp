from rest_framework import serializers

from finance.serializers import StudentsTrxsSerializer
from school.models import School,SchoolDeleteRequest
from school.serializers import TermSerializer, SessionSerializer
from academics.serializers import MiniClassRoomSerializer,MiniSchoolSectionSerializer,SubjectSerializer
from teacher.models import Teacher
from director.models import Director
from parent.models import Parents 
from staff.models import Staff
from core .models import BankDetails 
from authUser.serializers import MiniUserSerializer 
from school.models import SchoolPermission,SchoolRole

from django.db.models import FloatField, Sum, DecimalField ,Q ,OuterRef, Subquery
from django.db.models.functions import Coalesce
import json 
from finance.models import  StudentTransaction



class BankSerializer(serializers.ModelSerializer) : 
    class Meta:  
        model = BankDetails 
        fields ='__all__'
        read_only_fields = ['id', 'created_at']
        
 
class SchoolDeleteRequestSerialzer(serializers.ModelSerializer):
    class Meta:  
        model = SchoolDeleteRequest
        fields ='__all__'
        read_only_fields = ['id', 'requested_at']  

class ParentSchoolSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField(read_only =True)
    dashboardData = serializers.SerializerMethodField(read_only =True)
    sections = MiniSchoolSectionSerializer(many=True, read_only=True) # sections full 
    classrooms =   MiniClassRoomSerializer(many=True, read_only =  True) # classroom full data
    subjects = SubjectSerializer(many=True, read_only =  True)
    terms = TermSerializer(read_only=True,many=True)
    sessions = SessionSerializer(read_only=True,many=True)
    delete_requests = SchoolDeleteRequestSerialzer(read_only = True)
    
    class Meta:  
        model = School
        fields ='__all__'
        read_only_fields = ['id', 'joined_at','ref_id']
        write_only_fields = ['director']
    
    def get_logo(self, obj):
        return obj.logo.url if obj.logo else None
    
    def get_dashboardData(self, obj):
        # this will handle finance and academics data for parent dashbord
            student_ids = obj.students.values_list('id',flat=True)
            strxs = StudentTransaction.objects.filter( 
                student__school_id = obj.id,
                student_id__in = student_ids
            ).select_related(
                'student','payment_source'
            )
            
            latest_trx_subquery = (
                StudentTransaction.objects
                .filter(
                    student=OuterRef("student"), 
                    student_id__in = student_ids
                )
                .order_by("-created_at")
            )

            latest_trxs = StudentTransaction.objects.filter(
                id=Subquery(latest_trx_subquery.values("id")[:1]),
                student_id__in = student_ids

            )
            latest_balance_subquery = (
                StudentTransaction.objects
                .filter(student=OuterRef("student"))
                .order_by("-created_at")
                .values("net_balance")[:1]
            )
            trxs = strxs.filter(status__in  = ['PAID',]).select_related(
                    'payment_source'
                ).order_by(
                    "student_id",
                    "-created_at"
                ).distinct(
                    "student_id"
                ).annotate(
                    current_net_balance=Subquery(latest_balance_subquery,output_field=FloatField())
                    
                )
            data = StudentsTrxsSerializer(trxs.all(),many = True ).data
                

            total_net_bal = latest_trxs.aggregate(
                total_balance=Sum("net_balance")
            )["total_balance"] 
            
            total_paid = strxs.filter(transaction_type  = 'PAYMENT')
            tp = total_paid.aggregate(
                total=Coalesce(Sum('amount_paid'), 0,output_field=DecimalField())
            )
            paid_count = total_paid.distinct('student_id').count()
            return ({
                'studentTrxs' : data,
                "totalNetBalance" : total_net_bal ,
                "totalPaid" : tp['total'],
                "paidCount" : paid_count,
                
                "totalStudents" : obj.students.count(),
                'totalGirls' : obj.students.filter(gender = 'female').count(),
                'totalBoys' : obj.students.filter(gender = 'male').count(),
            })
           
            
class TeacherSchoolSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField(read_only =True)
    sections = MiniSchoolSectionSerializer(many=True, read_only=True) # sections full 
    classrooms =   MiniClassRoomSerializer(many=True, read_only =  True) # classroom full data
    subjects = SubjectSerializer(many=True, read_only =  True)
    terms = TermSerializer(read_only=True,many=True)
    sessions = SessionSerializer(read_only=True,many=True)
    delete_requests = SchoolDeleteRequestSerialzer(read_only = True)
    
    class Meta:  
        model = School
        fields ='__all__'
        read_only_fields = ['id', 'joined_at','ref_id']
        write_only_fields = ['director']
    
    def get_logo(self, obj):
        return obj.logo.url if obj.logo else None
    
class StaffSchoolSerializer(serializers.ModelSerializer):
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
            "inactive":obj.students.exclude(user__is_active = True).count(), # because student can exist with out user
            "males":obj.students.exclude(gender = 'males').count() ,
            "females":obj.students.exclude(gender = 'females').count()
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
            "males":obj.students.exclude(gender = 'males').count() ,
            "females":obj.students.exclude(gender = 'females').count(),
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
class TeacherSerializer(serializers.ModelSerializer) : 
    user = MiniUserSerializer(read_only=True)
    school = TeacherSchoolSerializer(read_only=True) 
    class Meta:  
        model = Teacher 
        fields ='__all__'
        read_only_fields = ['id', 'joined_at']

class MiniSchoolPermissionSerializer(serializers.ModelSerializer) :
    class Meta:
        model = SchoolPermission
        fields = ['id','school','name','description']
        read_only_fields = ['id','name']
    
class MiniSchoolRoleSerializer(serializers.ModelSerializer) :
    permissions = MiniSchoolPermissionSerializer(many=True, read_only=True)
    class Meta:
        model = SchoolRole
        fields = '__all__'
        read_only_fields = ['id']
class StaffSerializer(serializers.ModelSerializer):
    school = StaffSchoolSerializer()
    user = MiniUserSerializer(read_only=True)
    staff_role = MiniSchoolRoleSerializer(read_only =True)
            
    class Meta:
        model = Staff
        fields = '__all__'
        read_only_fields = ['id', 'joined_at']
        
        
class StudentSerializer(serializers.ModelSerializer):
    # school = SchoolSerializer()
    user = MiniUserSerializer(read_only=True)
    # class Meta:
    #     model = Student
    #     fields = '__all__' 

class ParentsSerializer(serializers.ModelSerializer):
    user = MiniUserSerializer(read_only=True)
    school = ParentSchoolSerializer(read_only=True)
    class Meta:
        model = Parents
        fields = '__all__'
        read_only_fields = ['id', 'joined_at']                      
                  