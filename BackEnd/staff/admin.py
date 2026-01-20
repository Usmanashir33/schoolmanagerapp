from django.contrib import admin

# Register your models here.
from .models import Staff
@admin.register(Staff)  
class StaffAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'school', 'role', 'staff_id', 'joined_at')
    search_fields = ('first_name', 'last_name', 'email', 'staff_id')
    list_filter = ('school', 'role', 'joined_at')   