from django.contrib import admin
from .models import Teacher
# Register your models here.
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display =["user","staff_id","school",'first_name','email',"joined_at"]
    search_fields =['user__username','staff_id','school__name','id']
   
   
   