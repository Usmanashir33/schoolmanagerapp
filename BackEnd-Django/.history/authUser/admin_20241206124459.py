from django.contrib import admin
from.models import User , KYC

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display =["id","username","phone_number","email","kyc_confirmed","log_with_otp""is_staff"]
    list_filter=[]
    list_editable =[]
    fieldsets = (
        (None, {
            'fields': (
                
            ),
        }),
    )
    
