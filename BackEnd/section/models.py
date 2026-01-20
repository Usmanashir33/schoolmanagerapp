from django.db import models
# Create your models here.
from django.db import models
import shortuuid
from school.models import School
from authUser.models import User
import os , uuid
from django.utils.translation import gettext_lazy as _  
from datetime import datetime
from director.models import Director
from core.models import  generate_unique_admission_number



# Create your models here.
class SchoolSection(models.Model) :
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=25)
    name = models.CharField(max_length=100) # Example: "SS1 A"
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="sections")
    joined_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.school.name}" 
