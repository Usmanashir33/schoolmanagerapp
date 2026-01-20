# Create your models here.
from django.db import models
import shortuuid
from authUser.models import User
import os , uuid
from django.utils.translation import gettext_lazy as _  
from datetime import datetime
from director.models import Director
from core.models import  generate_unique_admission_number



def upload_school_logo(instance,filename):
    ext = os.path.splitext(filename)[1]
    name = f"{instance.id}_logo{ext}"
    return os.path.join("schools/",name)

def upload_staff_pic(instance,filename):
    ext = os.path.splitext(filename)[1]
    name = f"{instance.id}_logo{ext}"
    return os.path.join("staffs/",name)

GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'), 
)


class School(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=25)
    ref_id= models.CharField(max_length=20, unique=True, editable=False)
    director = models.ForeignKey(Director, on_delete=models.PROTECT,related_name='directorschools',blank=True, null=True)
    
    name = models.CharField(max_length=255,unique=True) 
    email = models.EmailField(_("email"), max_length=254,unique=True)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)
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
class SchoolDeleteRequest(models.Model) :
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