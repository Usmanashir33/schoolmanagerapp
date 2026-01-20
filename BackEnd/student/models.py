from django.db import models
# Create your models here.
from django.db import models
import shortuuid
from authUser.models import User
from classroom.models import ClassRoom
import os , uuid
from django.utils.translation import gettext_lazy as _  
from datetime import datetime
from director.models import Director
from core.models import  generate_unique_admission_number

def upload_student_pic(instance,filename):
    ext = os.path.splitext(filename)[1]
    name = f"{instance.id}_logo{ext}"
    return os.path.join("students/",name)

GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'), 
)

# Create your models here.
class Student(models.Model) :
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=25)
    user = models.OneToOneField(User, on_delete=models.SET_NULL,blank=True,related_name='student', null=True)
    first_name = models.CharField(max_length=100,)
    last_name = models.CharField(max_length=100,)
    middle_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(unique=True,)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)    
    picture = models.ImageField(_("student pic"), upload_to= upload_student_pic ,default='student_default.png',blank=True,null=True)
    role = models.CharField(max_length=50,default='Student')
    class_room = models.ForeignKey(ClassRoom, on_delete=models.SET_NULL,related_name='students',blank=True, null=True)
    
    admission_number = models.CharField(max_length=120,null=True,blank=True, unique=True,editable=False)
    date_of_birth = models.DateField(null=True, blank=True)
    parent_phone = models.CharField(max_length=20, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    
    def save(self, *args, **kwargs):
        if not self.class_room :
            raise ValueError("Student must have a classroom before saving")
        if not self.admission_number:
            self.admission_number = generate_unique_admission_number(self.class_room.section.school.tag)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.first_name + " " + self.last_name