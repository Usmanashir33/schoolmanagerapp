from django.db import models

# Create your models here.
from django.db import models
import shortuuid
from authUser.models import User
import os 
from django.utils.translation import gettext_lazy as _  
from datetime import datetime
from django.db import transaction


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

import uuid

GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'), 
)
from django.db import models

class NumberCounter(models.Model):
    last_number = models.PositiveIntegerField(default=0)
    def __str__(self):
        return str(self.last_number)
    
    

def generate_unique_admission_number(tag,prefix=''):
    year = str(datetime.now().year)[-2:]
    with transaction.atomic():
        counter, created = NumberCounter.objects.select_for_update().get_or_create(id=1)
        counter.last_number += 1
        counter.save()
        unique_number = str(counter.last_number).zfill(4)

    return f"{tag}/{prefix}/{year}/{unique_number}" if prefix else f"{tag}/{year}/{unique_number}"

class School(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=25)
    ref_id= models.CharField(max_length=20, unique=True, editable=False)
    
    name = models.CharField(max_length=255,unique=True) 
    email = models.EmailField(_("email"), max_length=254,unique=True)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    
    # Director Details
    director = models.ForeignKey(User, on_delete=models.PROTECT,related_name='directorschools',blank=True, null=True)
    director_fullname = models.CharField(_("director name"), max_length=150,)
    director_email = models.EmailField(_("director email"), max_length=254, blank=True, null=True)
    director_phone = models.CharField(max_length=300, blank=True, null=True)
    
    logo = models.ImageField(upload_to=upload_school_logo,default='school_default.png', blank=True, null=True)
    tag = models.CharField(max_length=6, blank=True, null=True,unique=True)
    joined_at = models.DateTimeField(auto_now_add=True) 
    on_delete_request = models.BooleanField(default=False)

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
    
class SchoolSection(models.Model) :
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=25)
    name = models.CharField(max_length=100) # Example: "SS1 A"
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="sections")
    joined_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.school.name}" 

    
class Teacher(models.Model) :
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=25)
    user = models.OneToOneField(User, on_delete=models.SET_NULL,blank=True,related_name='teachers', null=True)
    first_name = models.CharField(max_length=100,)
    last_name = models.CharField(max_length=100,)
    middle_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(unique=True,)
    title= models.CharField(max_length=50, blank=True)  # Example: "Mr.", "Ms.", "Dr."
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    
    picture = models.ImageField(_("teacher pic"), upload_to= upload_teacher_pic ,default='teacher_default.png',null=True,blank=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="teachers")
    section = models.ManyToManyField(SchoolSection, related_name="teachers", blank=True,symmetrical=False,)
    
    staff_id = models.CharField(max_length=120, unique=True,blank=True,null=True,editable=False)
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.staff_id:
            self.staff_id = generate_unique_admission_number(self.school.tag, prefix='STAFF')
        super().save(*args, **kwargs)
        

    def __str__(self):
        return self.user.username
    
class ClassRoom(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=25)
    name = models.CharField(max_length=100)  # Example: "SS1 A"
    section = models.ForeignKey(SchoolSection, on_delete=models.CASCADE, related_name="classrooms", null=True,)
    class_teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.section.school.name}" 
    
class Student(models.Model) :
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=25)
    user = models.OneToOneField(User, on_delete=models.SET_NULL,blank=True,related_name='students', null=True)
    first_name = models.CharField(max_length=100,)
    last_name = models.CharField(max_length=100,)
    middle_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(unique=True,)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)    
    picture = models.ImageField(_("student pic"), upload_to= upload_student_pic ,default='student_default.png',blank=True,null=True)
    
    class_room = models.ForeignKey(ClassRoom, on_delete=models.SET_NULL,related_name='students',blank=True, null=True)
    admission_number = models.CharField(max_length=120,null=True,blank=True, unique=True,editable=False)
    date_of_birth = models.DateField(null=True, blank=True)
    parent_phone = models.CharField(max_length=20, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.admission_number:
            self.admission_number = generate_unique_admission_number(self.class_room.section.school.tag)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.first_name + " " + self.last_name
    
class Subject(models.Model) :
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=25)
    name = models.CharField(max_length=100)
    code= models.CharField(max_length=20, unique=True,null=True)
    class_room = models.ManyToManyField(ClassRoom, related_name="subjects",blank=True,symmetrical=False,)
    teacher = models.ManyToManyField(Teacher,related_name="subjects", blank=True,symmetrical=False,)
    added_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
class Parents(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=25)
    user = models.OneToOneField(User, on_delete=models.SET_NULL,blank=True,related_name='parents', null=True)
    first_name = models.CharField(max_length=100,)
    last_name = models.CharField(max_length=100,)
    middle_name = models.CharField(max_length=100, blank=True)
    family_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(unique=True,)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    schools = models.ManyToManyField(School, related_name="parents",symmetrical=False,blank=True,)
    students = models.ForeignKey(Student, related_name="parents", on_delete=models.SET_NULL, null=True,blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.first_name + " " + self.last_name
    class Meta:
        verbose_name = "Parent"
        verbose_name_plural = "Parents" 
        
class SchoolDeleteRequest(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=25)
    school = models.OneToOneField(School, on_delete=models.SET_NULL, related_name="delete_requests", null=True)
    reason = models.TextField()
    requested_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        self.school.on_delete_request = True
        self.school.save()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Delete Request for {self.school.name} at {self.requested_at}"