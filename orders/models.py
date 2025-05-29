from django.db import models
from django.conf import settings
from files.models import UploadedFile

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="کاربر")
    file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE, verbose_name="فایل سفارش داده‌شده")
    ordered_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ سفارش")
    is_paid = models.BooleanField(default=False, verbose_name="پرداخت شده؟")

    def __str__(self):
        return f"{self.user.phone} - {self.file.title}"

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"
        unique_together = ['user', 'file']
