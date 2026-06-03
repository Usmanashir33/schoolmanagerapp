from django.contrib import admin

# Register your models here.
from .models import SchoolSection

#--------------------------------------------------------------------------------------
#                                    SECTION ADMIN
#--------------------------------------------------------------------------------------
@admin.register(SchoolSection)
class SchoolSectionAdmin(admin.ModelAdmin):
    list_display =["name","school","joined_at"]
    search_fields =['name','school__name','id']

#--------------------------------------------------------------------------------------
#                                    CLASSROOM ADMIN
from .models import ClassRoom,PromotionLog
 
@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin) :
    list_display =["name","section","joined_at"]  
    search_fields =['name','section__name','id']
    
@admin.register(PromotionLog)
class PromotionLogAdmin(admin.ModelAdmin):
    list_display =["promoted_by","session","school"]

#--------------------------------------------------------------------------------------
#                                SUBJECT ADMIN
from .models import Subject

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display =["name","code","added_at",]
    search_fields =['name','code','id']
