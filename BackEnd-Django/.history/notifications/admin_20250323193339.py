from django.contrib import admin
from .models import MNotification

# Register your models here.
@admin.register(MNotification)
class MoneyNotificationAdmin(admin.ModelAdmin):
    '''Admin View for MoneyNotification'''
    list_display = ("transaction_type",'status','date')
    list_filter = ('status','date')