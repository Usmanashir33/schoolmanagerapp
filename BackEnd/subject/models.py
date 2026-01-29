from django.db import models
import os,uuid
from classroom.models import ClassRoom
from teacher.models import Teacher

# Create your models here.
class Subject(models.Model) :
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=25)
    name = models.CharField(max_length=100)
    code= models.CharField(max_length=20,null=True)
    credits =models.IntegerField(blank=True,null=True)
    class_room = models.ManyToManyField(ClassRoom, related_name="subjects",blank=True,symmetrical=False,)
    teacher = models.ManyToManyField(Teacher,related_name="subjects", blank=True,symmetrical=False,)
    added_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name + " " + self.code