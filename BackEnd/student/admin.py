from django.contrib import admin
from .models import Student, StudentClassEnrollment 
# Register your models here.

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display =["user","admission_number",'first_name','email',"joined_at"]
    search_fields =['user__username','admission_number','id']

@admin.register(StudentClassEnrollment)
class StudentClassEnrollmentAdmin(admin.ModelAdmin) :
    list_display = ["student","class_room","session","status"]
    search_fields = ['student__user__username','class_room__name','session__name']