from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import get_user_model,authenticate, login,logout
from django.contrib import messages

CustomUser = get_user_model()

class SignUpView(View):
    template_name = 'accounts/signup.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone = request.POST.get("phone")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # اعتبارسنجی اولیه
        if not all([first_name, last_name, phone, password1, password2]):
            return render(request, self.template_name, {
                'error': 'لطفاً تمام فیلدها را پر کنید!'
            })

        if password1 != password2:
            return render(request, self.template_name, {
                'error': 'رمز عبور و تکرار آن یکسان نیستند!'
            })

        if CustomUser.objects.filter(phone=phone).exists():
            return render(request, self.template_name, {
                'error': 'این شماره تلفن قبلاً ثبت شده است!'
            })

        try:
            CustomUser.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                password=password1  # از create_user استفاده کن تا رمز به درستی هش بشه
            )
            messages.success(request, 'ثبت‌نام با موفقیت انجام شد.')
            return redirect('accounts:login')  # یا صفحه دلخواه
        except Exception as e:
            return render(request, self.template_name, {
                'error': f'خطا در ثبت‌نام: {str(e)}'
            })



class LoginView(View):
    template_name = 'accounts/login.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        phone = request.POST.get("phone")
        password = request.POST.get("password")

        user = authenticate(request, phone=phone, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "ورود با موفقیت انجام شد.")
            return redirect('home')  # تغییر بده به صفحه مناسب
        else:
            return render(request, self.template_name, {
                'error': 'شماره تلفن یا رمز اشتباه است.'
            })


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('accounts:login')  # یا صفحه اصلی سایت