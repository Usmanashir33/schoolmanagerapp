from django.db import models
# Create your models here.
from django.db import models
import shortuuid
from section.models import SchoolSection
from teacher.models import Teacher
from authUser.models import User
import os , uuid
from django.utils.translation import gettext_lazy as _  
from datetime import datetime
from director.models import Director
from core.models import  generate_unique_admission_number

GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'), 
)

# Create your models here.
class ClassRoom(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=25)
    name = models.CharField(max_length=100)  # Example: "SS1 A"
    section = models.ForeignKey(SchoolSection, on_delete=models.CASCADE, related_name="classrooms", null=True,)
    class_teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.section.school.name}" 
    
