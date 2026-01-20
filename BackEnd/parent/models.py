from django.db import models
# Create your models here.
from django.db import models
import shortuuid
from authUser.models import User
import os , uuid
from django.utils.translation import gettext_lazy as _  
from datetime import datetime
from director.models import Director
from core.models import  generate_unique_admission_number
from school.models import *
from student.models import *


GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'), 
)
# Create your models here.
class Parents(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=25)
    user = models.OneToOneField(User, on_delete=models.SET_NULL,blank=True,related_name='parent', null=True)
    first_name = models.CharField(max_length=100,)
    last_name = models.CharField(max_length=100,)
    middle_name = models.CharField(max_length=100, blank=True)
    family_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(unique=True,)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True,default='male')
    schools = models.ManyToManyField(School, related_name="parents",symmetrical=False,blank=True,)
    students = models.ForeignKey(Student, related_name="parents", on_delete=models.SET_NULL, null=True,blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=50, default='Parent')
    def __str__(self):
        return self.first_name + " " + self.last_name
    class Meta:
        verbose_name = "Parent"
        verbose_name_plural = "Parents" 
 
        