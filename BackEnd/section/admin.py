from django.contrib import admin

# Register your models here.
from .models import SchoolSection

@admin.register(SchoolSection)
class SchoolSectionAdmin(admin.ModelAdmin):
    list_display =["name","school","joined_at"]
    search_fields =['name','school__name','id']

