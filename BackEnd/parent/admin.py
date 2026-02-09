from django.contrib import admin
from .models import Parents
# Register your models here.
@admin.register(Parents)
class ParentsAdmin(admin.ModelAdmin):
    list_display =["full_name","phone","email","joined_at",]
    search_fields =['user__username','phone','id','full_name']
