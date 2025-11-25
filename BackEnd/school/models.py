from django.db import models

# Create your models here.
from django.db import models
import shortuuid
from authUser.models import User
import os 
from django.utils.translation import gettext_lazy as _  
from datetime import datetime

def upload_school_logo(instance,filename):
    ext = os.path.splitext(filename)[1]
    name = f"{instance.id}_logo{ext}"
    return os.path.join("schools/",name)

def upload_student_pic(instance,filename):
    ext = os.path.splitext(filename)[1]
    name = f"{instance.id}_logo{ext}"
    return os.path.join("students/",name)

def upload_teacher_pic(instance,filename):
    ext = os.path.splitext(filename)[1]
    name = f"{instance.id}_logo{ext}"
    return os.path.join("teachers/",name)

def uuid():
    return shortuuid.uuid()

class School(models.Model):
    id = models.CharField(primary_key=True, default=uuid, editable=False, max_length=25)
    ref_id= models.CharField(max_length=20, unique=True, editable=False)
    
    director = models.ForeignKey(User, on_delete=models.DO_NOTHING,related_name='schools')
    name = models.CharField(max_length=255) 
    email = models.EmailField(_("email"), max_length=254,blank=True,unique=True)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    
    logo = models.ImageField(upload_to=upload_school_logo,default='school_default.png', blank=True, null=True)
    tag = models.CharField(max_length=6, blank=True, null=True,unique=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.ref_id:
            self.ref_id = self.generate_unique_sch_code('ref_id')
        super().save(*args, **kwargs)
        
    def generate_unique_sch_code(self, field, prefix='SCH'):
        alphabet = 'QERTYUIOPASDFGHKLZXCVBNM12451234567890'
        while True:
            code = shortuuid.ShortUUID(alphabet=alphabet).random(length=11)
            if not School.objects.filter(**{field: f"{prefix}-{code}"}).exists():
                return f"{prefix}-{code}"
        
    def __str__(self):
        return self.name
    
    
class SchoolSection(models.Model):
    id = models.CharField(primary_key=True, default=uuid, editable=False, max_length=25)
    name = models.CharField(max_length=100)  # Example: "SS1 A"
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="sections")
    joined_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.school.name}" 
    
class Teacher(models.Model) :
    id = models.CharField(primary_key=True, default=uuid, editable=False, max_length=25)
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING,related_name='teachers')
    picture = models.ImageField(_("teacher pic"), upload_to= upload_teacher_pic ,default='teacher_default.png',null=True,blank=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="teachers")
    section = models.ForeignKey(SchoolSection, on_delete=models.DO_NOTHING, related_name="teachers", null=True, blank=True)
    
    staff_id = models.CharField(max_length=120, unique=True,blank=True,null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.staff_id:
            self.staff_id = self.generate_unique_employee_number( )
        super().save(*args, **kwargs)
        
    # craete a function to generate unique employee_number for Teachers
    def generate_unique_employee_number(self,):
        def generate_employee_number(number):
            return str(number).zfill(3) 
        # get school tag from the student's class room
        prefix = self.school.tag
        # get current year fron date 
        year_last_2_digit = datetime.now().year[:2]
        count = Teacher.objects.filter(school=self.school).count()
        code = generate_employee_number(count + 1)
        new_emp_number = f"{prefix}/STAFF/{year_last_2_digit}/{code}"
        while True:
            if not Teacher.objects.filter(employee_number = new_emp_number).exists():
                return new_emp_number

    def __str__(self):
        return self.user
    
class ClassRoom(models.Model):
    id = models.CharField(primary_key=True, default=uuid, editable=False, max_length=25)
    name = models.CharField(max_length=100)  # Example: "SS1 A"
    section = models.ForeignKey(SchoolSection, on_delete=models.CASCADE, related_name="classrooms", null=True,)
    class_teacher = models.ForeignKey(Teacher, on_delete=models.DO_NOTHING, null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.school.name}" 
    
class Student(models.Model):
    id = models.CharField(primary_key=True, default=uuid, editable=False, max_length=25)
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    picture = models.ImageField(_("student pic"), upload_to= upload_student_pic ,default='student_default.png',blank=True,null=True)
    
    class_room = models.ForeignKey(ClassRoom, on_delete=models.DO_NOTHING,related_name='students')
    admission_number = models.CharField(max_length=120,null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    parent_phone = models.CharField(max_length=20, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.admission_number:
            self.admission_number = self.generate_unique_admission_number( )
        super().save(*args, **kwargs)
    # craete a function to generate unique admission number for students
    def generate_unique_admission_number(self,):
        def generate_admission_number(number):
            return str(number).zfill(4) 
        # get school tag from the student's class room
        prefix = self.class_room.section.school.tag
        # get current year fron date 
        year_last_2_digit = datetime.now().year[:2]
        count = Student.objects.filter(class_room__section__school=self.class_room.section.school).count()
        code = generate_admission_number(count + 1)
        new_adm_number = f"{prefix}/{year_last_2_digit}/{code}"
        while True:
            if not Student.objects.filter(admission_number = new_adm_number).exists():
                return new_adm_number 
        
    def __str__(self):
        return self.user
    
class Subject(models.Model) :
    id = models.CharField(primary_key=True, default=uuid, editable=False, max_length=25)
    name = models.CharField(max_length=100)
    code= models.CharField(max_length=20, unique=True,null=True)
    class_room = models.ManyToManyField(ClassRoom, related_name="subjects",blank=True,symmetrical=False,)
    teacher = models.ManyToManyField(Teacher,related_name="subjects", blank=True,symmetrical=False,)
    added_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name