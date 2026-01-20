from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Director 


# Register your models here.
@admin.register(Director )
class DirectorAdmin(admin.ModelAdmin):
    list_display = ('show_id', 'user', 'full_name', 'phone', 'email', 'joined_at')
    search_fields = ('user__username', 'user__email', 'phone')
    list_filter = ('joined_at',)
