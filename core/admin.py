from django.contrib import admin
from .models import ContactMessage

# Register your models here.

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at', 'user')
    search_fields = ('name', 'email', 'subject', 'message', 'user__username')
    readonly_fields = ('created_at',)
    list_per_page = 20

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "علامت‌گذاری به عنوان خوانده شده"

    actions = ['mark_as_read']
