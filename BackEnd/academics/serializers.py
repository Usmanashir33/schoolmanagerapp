from rest_framework import serializers
from .models import SchoolSection
from student .serializers import MiniStudentSerializer
from student.models import StudentClassEnrollment,Student
from teacher .serializers import MiniTeacherSerializer
from .models import ClassRoom


#------------------------------------------------------------------------------------
#                                       Mini Serializers 
#####################################################################################
class MiniClassRoomSerializer(serializers.ModelSerializer) :
    form_teacher = MiniTeacherSerializer(read_only =True)
    studentsCount = serializers.SerializerMethodField(read_only = True)
    teachersCount = serializers.SerializerMethodField(read_only = True)
    
    subjectsCount = serializers.SerializerMethodField(read_only = True)
    def get_subjectsCount(self,obj): 
        return obj.teaching_assignments.all().count()

    def get_studentsCount(self,obj):
        return obj.student_enrollments.filter(status__in=["active",'enrolled']).count()
    
    def get_teachersCount(self,obj):
        return obj.teaching_assignments.count()
    class Meta:  
        model = ClassRoom
        fields ='__all__'
        read_only_fields = ['id', 'form_teacher','name',]
class MiniSchoolSectionSerializer(serializers.ModelSerializer) :
    classesCount = serializers.SerializerMethodField(read_only = True)
    studentsCount = serializers.SerializerMethodField(read_only = True)
    teachersCount = serializers.SerializerMethodField(read_only = True)
    
    def get_classesCount(self,obj):
        return obj.classrooms.count()
    
    def get_studentsCount(self, obj):
        return StudentClassEnrollment.objects.filter(
            class_room__section__id=obj.id,
            status__in=["active", "enrolled"]
        ).count()

    def get_teachersCount(self, obj):
        return Teacher.objects.filter(
            subjects__teaching_assignments__classroom__section__id=obj.id
        ).distinct().count()
    
    class Meta:  
        model = SchoolSection 
        fields ='__all__'
        read_only_fields = ['id', 'joined_at']

#------------------------------------------------------------------------------------
#                                    SECTION SERIALIZERS
#------------------------------------------------------------------------------------
class SchoolSectionCreateUpdateSerializer(serializers.ModelSerializer):
    classesCount = serializers.SerializerMethodField(read_only = True)
    studentsCount = serializers.SerializerMethodField(read_only = True)
    teachersCount = serializers.SerializerMethodField(read_only = True)
    
    def get_studentsCount(self, obj):
        return StudentClassEnrollment.objects.filter(
            class_room__section=obj,
            status__in=["active", "enrolled"]
        ).count()

    def get_teachersCount(self, obj):
        return Teacher.objects.filter(
            subjects__class_rooms__section=obj
        ).distinct().count()
        
    def get_teachersCount(self,obj):
        teachers = Teacher.objects.filter(
            subjects__class_rooms__section=obj
        ).distinct()
        return teachers.count()

    class Meta:  
        model = SchoolSection 
        fields ='__all__'
        read_only_fields = ['id', 'joined_at']
        
class SchoolSectionDetailSerializer(serializers.ModelSerializer):
    students = serializers.SerializerMethodField(read_only = True)
    teachers = serializers.SerializerMethodField(read_only = True)
    
    def get_students(self,obj):
        students = StudentClassEnrollment.objects.filter(
            class_room__section=obj,
            status__in=["active", "enrolled"]
        )[:15]
        return MiniStudentSerializer(students,many=True).data
    
    def get_teachers(self, obj):
        teachers = Teacher.objects.filter(
            subjects__teaching_assignments__classroom__section=obj
        ).distinct()[:15]
        return MiniTeacherSerializer(teachers,many=True).data

    class Meta:  
        model = SchoolSection 
        fields ='__all__'
        read_only_fields = ['id', 'joined_at']
        

#--------------------------------------------------------------------------------------
#                                    CLASSROOM SERIALIZERS

from .models import ClassRoom ,PromotionLog
class ClassRoomDetailSerializer(serializers.ModelSerializer) :
    form_teacher = MiniTeacherSerializer(read_only =True)
    students = serializers.SerializerMethodField(read_only = True)
    teachers = serializers.SerializerMethodField(read_only = True)
    subjects = serializers.SerializerMethodField(read_only = True)
    studentsCount = serializers.IntegerField(read_only=True)
    teachersCount = serializers.IntegerField(read_only=True)
    
    def get_subjects(self,obj): 
        ass = obj.teaching_assignments.all()
        # return subjects.values('subject_id',)
        return [{
            'id':s.subject.id,
            "teacher":{
                "id":s.teacher.id,
                "name":f"{s.teacher.title} {s.teacher.first_name} {s.teacher.last_name}",
                "staff_id":s.teacher.staff_id,
            }
        } for s in ass]
    
    def get_students(self,obj):
        studentIds = obj.student_enrollments.filter(status__in=["active",'enrolled']).values_list('student',flat=True)
        students = Student.objects.filter(id__in = studentIds)[:15]
        return MiniStudentSerializer(students,many=True).data
    
    def get_teachers(self,obj) :
        teachers_map_ids = obj.teaching_assignments.values_list('teacher__id', flat=True)
        teachers = Teacher.objects.filter(school = obj.section.school,id__in = teachers_map_ids)[:15]
        return MiniTeacherSerializer(teachers,many=True).data
    class Meta:  
        model = ClassRoom 
        fields ='__all__'
        read_only_fields = ['id', 'form_teacher','name',]
        
        
class ClassRoomCreateUpdateSerializer(serializers.ModelSerializer) :
    form_teacher = MiniTeacherSerializer(read_only =True)
    studentsCount = serializers.SerializerMethodField(read_only = True)
    teachersCount = serializers.SerializerMethodField(read_only = True)
    subjects = serializers.SerializerMethodField(read_only = True)
    def get_subjects(self,obj): 
        subjects = obj.teaching_assignments.all()
        return subjects.values('subject__id')
    
    def get_studentsCount(self,obj):
        return obj.student_enrollments.filter(status__in=["active",'enrolled']).count()
    
    def get_teachersCount(self,obj):
        return obj.teaching_assignments.values_list('teacher', flat=True).distinct().count()
    class Meta:  
        model = ClassRoom 
        fields ='__all__'
        read_only_fields = ['id', 'joined_at']

class PromotionLogSerializer(serializers.ModelSerializer) :
    class Meta:  
        model = PromotionLog
        fields ='__all__'
        read_only_fields = ['id', 'created_at']
        
        
        
        
#------------------------------------------------------------------------------------------------
#                           SUBJECT SERIALIZERS
#------------------------------------------------------------------------------------------------
from .models import Subject,ClassRoom
from teacher.models import Teacher
from django.db import transaction

    
class SubjectSerializer(serializers.ModelSerializer) :
    teachers= serializers.SerializerMethodField(read_only = True)
    classes = serializers.SerializerMethodField(read_only = True)
    def get_classes(self,obj) :
        classes_map = obj.teaching_assignments.values_list('classroom__id', flat=True).distinct()
        return classes_map
    def get_teachers(self,obj) :
        teachers_map = obj.teachers.values('id', "first_name", "last_name","title",'staff_id')
        return teachers_map
    class Meta:  
        model = Subject   
        fields ='__all__' 
        read_only_fields = ['id', 'added_at']
    
class SubjectDetailSerializer(serializers.ModelSerializer) :
    teachers= serializers.SerializerMethodField(read_only = True)
    classes = serializers.SerializerMethodField(read_only = True)
    def get_classes(self,obj) :
        classes_map = obj.teaching_assignments.values_list('classroom__id', flat=True).distinct()
        return classes_map
    
    def get_teachers(self,obj) : 
        teachers = obj.teachers
        return MiniTeacherSerializer(teachers ,many=True).data
    class Meta:  
        model = Subject 
        fields ='__all__' 
        read_only_fields = ['id', 'added_at','class_rooms','teachers']
        
class SubjectCreateUpdateSerializer(serializers.ModelSerializer) :
    teachers= serializers.SerializerMethodField(read_only = True)
    classes = serializers.SerializerMethodField(read_only = True)
    def get_classes(self,obj) :
        classes_map = obj.teaching_assignments.values_list('classroom__id', flat=True).distinct()
        return classes_map
    
    def get_teachers(self,obj) :
        teachers_map = obj.teachers.values('id', "first_name", "last_name","title",'staff_id')
        return teachers_map
    class Meta:  
        model = Subject 
        fields ='__all__' 
        read_only_fields = ['id', 'added_at','class_rooms','teachers']
        
    def create(self, validated_data) :
        request = self.context["request"]
        school_id = self.context["school_id"]
        teachers_ids = request.data.get("teachersIds", [])
        teachers = Teacher.objects.filter(school_id = school_id, id__in = teachers_ids)
        
        with transaction.atomic():
            subject = Subject.objects.create(**validated_data)
            if teachers.exists() :
                subject.teachers.set(teachers)
            subject.save()
        return subject 
    
    def update(self, instance, validated_data):
        request = self.context["request"]
        school_id = self.context["school_id"]
        
        teachers_ids = request.data.get("teachersIds", [])
        

        with transaction.atomic():
            # update subject 
            for field ,value in validated_data.items() :
                setattr(instance,field,value)
            
            teachers = Teacher.objects.filter(school_id = school_id, id__in = teachers_ids)
            if teachers.exists()  :
                instance.teachers.set(teachers) 
                
            
            instance.save()
                
        return instance 
