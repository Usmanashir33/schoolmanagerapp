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
from school.models import School

def upload_staff_pic(instance,filename):
    ext = os.path.splitext(filename)[1]
    name = f"{instance.id}_logo{ext}"
    return os.path.join("staffs/",name)

GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'), 
)
NSA_CHOICES = (
    ('security', 'Security'),
    ('cleaner', 'Cleaner'),
    ('driver', 'Driver'),
)
NSA_RANKS = (
    ('header', 'Header'),
    ('vice', 'Vice'),
    ('standerd', 'Standerd'),
)
# craete activity role model
class ActivityRole(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=25)
    role = models.CharField(max_length=100, choices=NSA_CHOICES, default='security')
    rank = models.CharField(max_length=100, choices=NSA_RANKS, default='standerd')
    active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    date_assined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role} - {self.rank}"

# Create your models here.
class Staff(models.Model) :
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=25)
    user = models.OneToOneField(User, on_delete=models.CASCADE,blank=True,related_name='staff', null=True)
    
    first_name = models.CharField(max_length=100,)
    last_name = models.CharField(max_length=100,)
    middle_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(unique=True,blank=True,null=True)
    title= models.CharField(max_length=50, blank=True)  # Example: "Mr.", "Ms.", "Dr."
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True,default='male')
    
    picture = models.ImageField(_("staff pic"), upload_to= upload_staff_pic ,default='staff_default.png',null=True,blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="staffs", blank=True, null=True)
    role = models.CharField(max_length=100, blank=True,default='Staff') 
    activity_role = models.ForeignKey(ActivityRole, on_delete=models.SET_NULL, related_name="roles", blank=True, null=True)
    address = models.TextField(blank=True)
    staff_id = models.CharField(max_length=120, unique=True,blank=True,null=True,editable=False)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.staff_id:
            self.staff_id = generate_unique_admission_number(self.school.tag, prefix='NAS')
        super().save(*args, **kwargs)
        

    def __str__(self):
        return self.staff_id
    
