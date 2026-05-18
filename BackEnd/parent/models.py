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


GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'), 
)
# Create your models here. 
class Parents(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length = 255)
    user = models.OneToOneField(User, on_delete=models.SET_NULL,blank=True,related_name='parent', null=True)
    full_name = models.CharField(blank = True ,max_length=100,)
    email = models.EmailField(unique=True) 
    relation_ship = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True,default='male')
    school = models.ForeignKey(School, on_delete=models.CASCADE,null=True,blank=True,related_name='parents')
    joined_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=50, default='Parent')
    
    def __str__(self):
        return self.full_name 
    class Meta:
        verbose_name = "Parent"
        verbose_name_plural = "Parents" 
 
          