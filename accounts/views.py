from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import get_user_model,authenticate, login,logout
from django.contrib import messages

CustomUser = get_user_model()

class SignUpView(View):
    def get(self, request):
        return redirect('core:home')

    def post(self, request):
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone = request.POST.get("phone")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # اعتبارسنجی اولیه
        if not all([first_name, last_name, phone, password1, password2]):
            return redirect('/?signup_error=empty')

        if password1 != password2:
            return redirect('/?signup_error=notmatch')

        if CustomUser.objects.filter(phone=phone).exists():
            return redirect('/?signup_error=exists')

        try:
            CustomUser.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                password=password1
            )
            messages.success(request, 'ثبت‌نام با موفقیت انجام شد.')
            return redirect('core:home')
        except Exception as e:
            return redirect('/?signup_error=fail')



class LoginView(View):
    def get(self, request):
        return redirect('core:home')

    def post(self, request):
        phone = request.POST.get("phone")
        password = request.POST.get("password")

        user = authenticate(request, phone=phone, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "ورود با موفقیت انجام شد.")
            return redirect('core:home')
        else:
            return redirect('/?login_error=1')


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('accounts:login')  # یا صفحه اصلی سایت