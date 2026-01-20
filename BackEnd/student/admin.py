from django.contrib import admin
from .models import Student 
# Register your models here.

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display =["user","admission_number","class_room",'first_name','email',"joined_at"]
    search_fields =['user__username','admission_number','class_room__name','id']

