from django.db import models

class UploadedFile(models.Model):
    FILE_TYPES = [
        ('pdf', 'PDF'),
        ('word', 'Word'),
        ('excel', 'Excel'),
        ('other', 'سایر'),
    ]

    title = models.CharField(max_length=255, verbose_name="عنوان فایل")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    file = models.FileField(upload_to='uploaded_files/', verbose_name="فایل")
    file_type = models.CharField(max_length=10, choices=FILE_TYPES, verbose_name="نوع فایل")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ آپلود")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "فایل آپلودی"
        verbose_name_plural = "فایل‌های آپلودی"
