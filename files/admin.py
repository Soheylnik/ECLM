from django.contrib import admin
from .models import UploadedFile, Download, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('title', 'file_type', 'category', 'uploaded_at', 'is_free', 'price', 'project_manager', 'file_size')
    search_fields = ('title', 'project_manager__first_name', 'project_manager__last_name')
    list_filter = ('file_type', 'is_free', 'category')
    exclude = ('slug',)

@admin.register(Download)
class DownloadAdmin(admin.ModelAdmin):
    list_display = ('user', 'file', 'downloaded_at')
    search_fields = ('user__username', 'file__title')
    list_filter = ('downloaded_at',)
