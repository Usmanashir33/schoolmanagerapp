from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(BankDetails)
class TeacherBankDetailsAdmin(admin.ModelAdmin ):
    list_display =["account_number","bank_name"]