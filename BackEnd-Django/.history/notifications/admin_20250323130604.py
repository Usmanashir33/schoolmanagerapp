from django.contrib import admin
from .mode

# Register your models here.
@admin.register(MoneyNotification)
class MoneyNotificationAdmin(admin.ModelAdmin):
    '''Admin View for MoneyNotification'''

    list_display = ('',)
    list_filter = ('',)
    inlines = [
        Inline,
    ]
    raw_id_fields = ('',)
    readonly_fields = ('',)
    search_fields = ('',)
    date_hierarchy = ''
    ordering = ('',)