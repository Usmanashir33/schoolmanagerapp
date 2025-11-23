from django.contrib import admin
from .models import Notification

# Register your models here.
@admin.register(Notification)
class MoneyNotificationAdmin(admin.ModelAdmin):
    '''Admin View for MoneyNotification'''
    list_display = ("titl','date')
    list_filter = ('status','date')