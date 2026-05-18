from django.contrib import admin
from .models import ClassRoom,PromotionLog

 
@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display =["name","section","joined_at"]
    search_fields =['name','section__name','id']
    
@admin.register(PromotionLog)
class PromotionLogAdmin(admin.ModelAdmin):
    list_display =["promoted_by","session","school"]

     