from django.db import models

# Create your models here.
from django.db import models
import shortuuid
from authUser.models import User
import os , uuid
from django.utils.translation import gettext_lazy as _  
from datetime import datetime
from django.db import transaction
from director.models import Director
from django.db import models
from school.models import School
from section.models import SchoolSection 
from classroom.models import ClassRoom
from core.models import  generate_unique_admission_number , BankDetails


def upload_teacher_pic(instance,filename):
    ext = os.path.splitext(filename)[1]
    name = f"{instance.id}_logo{ext}"
    return os.path.join("teachers/",name)

GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'), 
)
from django.db import models


# Create your models here.
class DisplinaryRecord(models.Model):
    SEVERITY_CHOICES = (
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    teacher = models.ForeignKey("Teacher", on_delete=models.SET_NULL, related_name="disciplinaryRecords",null=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    severity = models.CharField(max_length=10,choices=SEVERITY_CHOICES,default='Low'
    )
    
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.severity})"
class Teacher(models.Model) :
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length = 255)
    user = models.OneToOneField(User, on_delete=models.SET_NULL,blank=True,related_name='teacher', null=True)
    
    first_name = models.CharField(max_length=100,) 
    last_name = models.CharField(max_length=100,)
    middle_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(unique=True,null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES , blank=True,default='male')
    title= models.CharField(max_length=50, blank=True)  # Example: "Mr.", "Ms.", "Dr."
    picture = models.ImageField(_("teacher pic"), upload_to= upload_teacher_pic ,default='teacher_default.png',null=True,blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True,unique=True,null=True)
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="teachers")
    class_room = models.ManyToManyField(ClassRoom,  related_name="teachers", blank=True,symmetrical=False,)
    form_class = models.ForeignKey(ClassRoom, on_delete=models.SET_NULL, null=True, related_name="form_teacher", blank=True)
    
    role = models.CharField(max_length=50,default='Teacher')      
    nin = models.CharField(max_length=50,blank=True)      
    salary = models.CharField(blank=True,max_length=20,)     
    bank_details = models.OneToOneField(BankDetails,on_delete=models.SET_NULL,related_name= 'user',blank=True,null=True)
    
    address = models.CharField(max_length=255,blank=True,null=True)
    staff_id = models.CharField(max_length=120, unique=True,blank=True,null=True,editable=False)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.staff_id:
            self.staff_id = generate_unique_admission_number(self.school.tag, prefix='STAFF')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username if self.user else "Anonymous Teacher"  
    def full_name(self) :
        return f"{self.first_name} {self.last_name} {self.middle_name}"