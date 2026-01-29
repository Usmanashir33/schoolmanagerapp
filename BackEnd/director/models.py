
from django.db import models
import os, uuid
from authUser.models import User
from django.utils.translation import gettext_lazy as _


def upload_director_pic(instance,filename):
    ext = os.path.splitext(filename)[1]
    name = f"{instance.id}_logo{ext}"
    return os.path.join("directors/",name)
GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'), 
)

# Create your models here.
class Director(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=25)
    user = models.OneToOneField(User, on_delete=models.SET_NULL,blank=True,related_name='director', null=True)
    title =  models.CharField(max_length=100,blank=True)
    first_name = models.CharField(max_length=100,)
    last_name = models.CharField(max_length=100,) 
    middle_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(unique=True,)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True,default='male')
    phone = models.CharField(max_length=20, blank=True)
    picture = models.ImageField(_("director pic"), upload_to= upload_director_pic ,default='director_default.png',null=True,blank=True)
    role = models.CharField(max_length=100, blank=True ,default='Director')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.first_name + " " + self.last_name
    def show_id(self) :   
        return  f"{str(self.id)[:6]}..."
    def full_name(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}"  
    class Meta:
        verbose_name = "Director"
        verbose_name_plural = "Directors"