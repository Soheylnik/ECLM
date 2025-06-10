from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse
import re

def create_slug(text):
    # تبدیل حروف فارسی به معادل انگلیسی
    persian_to_english = {
        'ا': 'a', 'ب': 'b', 'پ': 'p', 'ت': 't', 'ث': 's', 'ج': 'j', 'چ': 'ch',
        'ح': 'h', 'خ': 'kh', 'د': 'd', 'ذ': 'z', 'ر': 'r', 'ز': 'z', 'ژ': 'zh',
        'س': 's', 'ش': 'sh', 'ص': 's', 'ض': 'z', 'ط': 't', 'ظ': 'z', 'ع': 'a',
        'غ': 'gh', 'ف': 'f', 'ق': 'gh', 'ک': 'k', 'گ': 'g', 'ل': 'l', 'م': 'm',
        'ن': 'n', 'و': 'v', 'ه': 'h', 'ی': 'y', 'ئ': 'y', 'ء': 'a',
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9',
        ' ': '-', '_': '-', '.': '-', '/': '-', '\\': '-',
    }
    
    # تبدیل متن به حروف کوچک
    text = text.lower()
    
    # تبدیل حروف فارسی به انگلیسی
    for persian, english in persian_to_english.items():
        text = text.replace(persian, english)
    
    # حذف کاراکترهای غیر مجاز
    text = re.sub(r'[^a-z0-9-]', '', text)
    
    # حذف خط تیره‌های تکراری
    text = re.sub(r'-+', '-', text)
    
    # حذف خط تیره از ابتدا و انتها
    text = text.strip('-')
    
    return text

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام دسته‌بندی")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="اسلاگ")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = create_slug(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ['name']

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
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="دسته‌بندی")
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
