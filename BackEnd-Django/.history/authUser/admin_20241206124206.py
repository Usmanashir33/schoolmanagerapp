from django.contrib import admin
from.models import User , KYC

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display =[]
    list_filter=[]
    list_editable =[]
    fi
    
