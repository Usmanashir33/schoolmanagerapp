from django.contrib import admin
from.models import User , KYC

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display =["id","username","phone_number","email","kyc_confirmed","log_with_otp","is_staff"]
    list_filter=['date','email']
    list_filter=['id','username','email','phonenumber']
    list_editable =["kyc_confirmed","email_varified","log_with_otp","lock_password","is_staff",'transection_permission']
    fieldsets = (
        ("User Details", {
            'fields': (
                "username","phone_number","email",
            ),
        }),
        ("User limitations", {
            'fields': (
                "kyc_confirmed","email_varified",
                "log_with_otp","lock_password",
                "is_staff",'is_superuser',
                'transection_permission'
            ),
        }),
        ("User Security", {
            'fields': (
                'lock_password','kyc_submitted'
            ),
        }),
    )
    
