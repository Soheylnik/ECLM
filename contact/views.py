from django.views import View
from django.shortcuts import render

class ContactView(View):
    template_name = 'contact/contact.html'  # فرضا یه صفحه ساده نمایش

    def get(self, request):
        # فقط رندر کردن صفحه بدون فرم
        return render(request, self.template_name)
