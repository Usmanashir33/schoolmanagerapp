from django.contrib import admin
from.models import User , KYC

# Register your models here.
@admin.register()
class Admin(admin.ModelAdmin):
    
