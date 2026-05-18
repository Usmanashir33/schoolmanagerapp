from django.contrib import admin
from .models import School, Session, Term,FinanceSettings,SchoolRole,SchoolPermission


# Register your models here.
@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display =["name","tag","ref_id","joined_at"]
    search_fields =['name','tag','id',"ref_id"]
    
@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display =["name","start_date","end_date","is_current"]
    search_fields =['name','id']
@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display =["name","start_date","end_date","is_current"]
    search_fields =['name','id']
@admin.register(FinanceSettings)
class FinanceSettingsAdmin(admin.ModelAdmin):
    list_display =['school',"onlinePayment","paymentDueDate"]

@admin.register(SchoolRole)
class SchoolRoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'school','description',]
    search_fields = ['name', 'school__name']
@admin.register(SchoolPermission)
class SchoolPermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'school','description',]
    search_fields = ['name', 'school__name']