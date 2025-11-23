from django.contrib import admin
from .models import MoneyNotification

# Register your models here.
@admin.register(MoneyNotification)
class MoneyNotificationAdmin(admin.ModelAdmin):
    '''Admin View for MoneyNotification'''

    list_display = ("transaction_type",'status')
    list_filter = ('',)