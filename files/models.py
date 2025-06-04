from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse

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
    project_manager = models.CharField(max_length=255, verbose_name="مدیر پروژه")
    is_free = models.BooleanField(default=False, verbose_name="رایگان؟")
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="قیمت (ریال)", null=True, blank=True)
    file_size = models.PositiveBigIntegerField(editable=False, null=True, blank=True, verbose_name="اندازه فایل (بایت)")
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="اسلاگ")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug or self.slug == '':
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while UploadedFile.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        if self.file:
            self.file_size = self.file.size
        if self.is_free:
            self.price = 0
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('files:file-detail', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = "فایل آپلودی"
        verbose_name_plural = "فایل‌های آپلودی"

class Download(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='downloads')
    file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE, related_name='downloads')
    downloaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'file')
        ordering = ['-downloaded_at']
