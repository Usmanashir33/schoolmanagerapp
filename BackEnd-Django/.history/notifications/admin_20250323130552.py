from django.contrib import admin

# Register your models here.
@admin.register(Mone)
class MoneAdmin(admin.ModelAdmin):
    '''Admin View for Mone'''

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