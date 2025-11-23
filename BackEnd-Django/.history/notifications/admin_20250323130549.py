from django.contrib import admin

# Register your models here.
@admin.register(M)
class MAdmin(admin.ModelAdmin):
    '''Admin View for M'''

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