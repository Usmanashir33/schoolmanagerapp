from django.contrib import admin
from .models import School


# Register your models here.
@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display =["name","tag","ref_id","joined_at"]
    search_fields =['name','tag','id',"ref_id"]
    
