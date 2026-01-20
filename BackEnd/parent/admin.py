from django.contrib import admin
from .models import Parents
# Register your models here.
@admin.register(Parents)
class ParentsAdmin(admin.ModelAdmin):
    list_display =["family_name","phone",'first_name',"joined_at",]
    search_fields =['user__username','phone','id','family_name']
