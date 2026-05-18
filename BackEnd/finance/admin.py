from django.contrib import admin
from .models import ClassFeeSetting, PaymentInitiation, StudentTransaction

# # Register your models here.
# @admin.register(ClassFeeSetting)
# class ClassFeeSettingAdmin(admin.ModelAdmin):
#     list_display = ('id', 'school', 'name', 'amount', 'created_at', 'updated_at')
#     list_filter = ('school',)
#     search_fields = ('name',)
    
@admin.register(PaymentInitiation)
class PaymentInitiationAdmin(admin.ModelAdmin):
    list_display = ('id', 'school','ref_number', 'payer', 'session', 'term', 'total_amount',)
    list_filter = ('school', 'session', 'term')


@admin.register(StudentTransaction)
class StudentTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'class_room', 'session', 'term', 'total_amount', 'amount_paid', 'net_balance', 'transaction_type', 'status', 'created_at')
