from django.contrib import admin
from .models import ClassRoom

 
@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display =["name","section","joined_at"]
    search_fields =['name','section__name','id']

     