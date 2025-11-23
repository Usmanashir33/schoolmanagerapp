from django.contrib import admin
from .models import Account ,MoneyTransaction,AccountNumber,W

# Register your models here.
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display =["current_account_number","account_id","account_balance","account_status"]
    list_filter=["account_status",]
    search_fields =["account_id",]

@admin.register(AccountNumber)
class AccountNumberAdmin(admin.ModelAdmin):
    list_display = ["account_number","bank_name"]
    search_fields =["account_number",]
    
@admin.register(MoneyTransaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display=['trx_id','status','amount','net_charges','transaction_type','payment_type']
    list_filter=["trx_id",'payment_type']
    search_fields =["trx_id","id"]
    
@admin.register(MoneyTransaction)
class TransactionAdmin(admin.ModelAdmin):
    fie