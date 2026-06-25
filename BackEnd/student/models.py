from django.db import models
# Create your models here.
from django.db import models
import shortuuid
from teacher.models import Teacher
from authUser.models import User
from academics.models import ClassRoom,Subject
import os , uuid
from django.utils.translation import gettext_lazy as _  
from datetime import datetime
from director.models import Director
from school.models import School , Session , Term
from parent.models import Parents
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
class StudentClassEnrollment(models.Model):
    student     = models.ForeignKey('Student', on_delete=models.SET_NULL, related_name='class_rooms', null=True,db_index=True)
    class_room  = models.ForeignKey(ClassRoom, related_name='student_enrollments', on_delete=models.SET_NULL, null=True,db_index=True)
    session = models.ForeignKey(Session,blank=True,null=True,on_delete=models.SET_NULL,db_index=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    date_left  =  models.DateTimeField(null=True, blank=True) 

    status = models.CharField( 
        choices = [
            ('active', 'Active'), # currently enrolled and attending classes
            ('promoted', 'Promoted')  , # promoted to next class but not yet attending classes
            ('transferred', 'Transferred')  , # trasferred to next class from another class 
            ('demoted', 'Demoted'), # demoted to previous class but not yet attending classes
            ('enrolled', 'Enrolled'), # newly enrolled but not yet attending classes
            ('withdrawn', 'Withdrawn') # withdrawn from the class and not attending classes
        ],default='enrolled' ,max_length=20, db_index=True
    )
    class Meta:
        indexes = [
            models.Index(fields=['student','status']),
            models.Index(fields=['student', 'class_room', 'status']),
        ]

class Student(models.Model) :
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length = 255)
    user = models.OneToOneField(User, on_delete=models.SET_NULL,blank=True,related_name='student', null=True)
    
    first_name = models.CharField(max_length=100, db_index=True) 
    last_name = models.CharField(max_length=100, db_index=True)  
    middle_name = models.CharField(max_length=100, blank=True,)  
    phone = models.CharField(max_length=100, blank=True,unique=True,null=True, db_index=True)  
    email = models.EmailField(db_index=True,blank=True, null=True) 
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)    
    picture = models.ImageField(_("student pic"), upload_to= upload_student_pic ,default='student_default.png',blank=True,null=True)
    
    role = models.CharField(max_length=50, default='Student', db_index=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="students", blank=True, null=True)
    
    admission_number = models.CharField(max_length=120,null=True,blank=True, unique=True,editable=False)
    
    date_of_birth = models.DateField(null=True, blank=True) 
    guardian = models.ForeignKey(Parents, on_delete=models.SET_NULL, related_name="children", blank=True, null=True)
    joined_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['school', 'admission_number']),
            models.Index(fields=['school', 'first_name']),
            models.Index(fields=['school', 'joined_at']),
        ]
        # ordering=['joined_at']
        ordering = ['joined_at']
    def save(self, *args, **kwargs):
        if not self.admission_number:
            self.admission_number = generate_unique_admission_number(self.school.tag)
        super().save(*args, **kwargs)
    
    def full_name(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}".strip()
    
    def __str__(self):
        return self.first_name + " " + self.last_name
    
