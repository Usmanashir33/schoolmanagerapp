from django.contrib import admin
from .models import School,SchoolSection,ClassRoom,Student,Teacher,Subject,Parents


# Register your models here.
@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display =["name","tag","ref_id","joined_at"]
    search_fields =['name','tag','id',"ref_id"]
    
@admin.register(SchoolSection)
class SchoolSectionAdmin(admin.ModelAdmin):
    list_display =["name","school","joined_at"]
    search_fields =['name','school__name','id']

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display =["user","staff_id","school",'first_name','email',"joined_at"]
    search_fields =['user__username','staff_id','school__name','id']
    
@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display =["name","section","class_teacher","joined_at"]
    search_fields =['name','section__name','class_teacher','id']
    
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display =["user","admission_number","class_room",'first_name','email',"joined_at"]
    search_fields =['user__username','admission_number','class_room__name','id']
    
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display =["name","code","added_at",]
    search_fields =['name','code','id']
    
@admin.register(Parents)
class ParentsAdmin(admin.ModelAdmin):
    list_display =["family_name","phone",'first_name',"joined_at",]
    search_fields =['user__username','phone','id','family_name']