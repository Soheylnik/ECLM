from django.views.generic import TemplateView, ListView, DetailView
from django.shortcuts import render, redirect, get_object_or_404
from files.models import UploadedFile, Download, Category
from django.core.paginator import Paginator
from django.utils.text import slugify
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from files.forms import UploadedFileForm
from django.contrib import messages
from .models import ContactMessage

class HomeView(TemplateView):
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        files = UploadedFile.objects.all().order_by('-uploaded_at')
        
        # اطمینان از وجود slug برای همه محصولات
        for file in files:
            if not file.slug:
                base_slug = slugify(file.title)
                slug = base_slug
                counter = 1
                while UploadedFile.objects.filter(slug=slug).exclude(pk=file.pk).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                file.slug = slug
                file.save()
        
        context['files'] = files
        
        # محاسبه تعداد محصولات در هر دسته‌بندی
        categories = {}
        for category in Category.objects.all():
            count = UploadedFile.objects.filter(category=category).count()
            categories[category.name] = count
        
        context['categories'] = categories
        return context

class ContactView(TemplateView):
    template_name = 'contact/contact.html'
    def get(self, request):
        return render(request, self.template_name)

class JobDetailsView(DetailView):
    model = UploadedFile
    template_name = 'core/jobdetails.html'
    context_object_name = 'file'

    def get_object(self):
        return get_object_or_404(UploadedFile, slug=self.kwargs['slug'])

class SearchGridView(TemplateView):
    template_name = 'core/search-grid.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        files_qs = UploadedFile.objects.all()
        
        # Ensure all files have a slug
        for f in files_qs:
            if not f.slug:
                base_slug = slugify(f.title)
                slug = base_slug
                counter = 1
                while UploadedFile.objects.filter(slug=slug).exclude(id=f.id).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                f.slug = slug
                f.save()

        # Search logic
        request = self.request
        keyword = request.GET.get('keyword', '').strip()
        file_type = request.GET.get('file_type', '').strip()

        if keyword:
            files_qs = files_qs.filter(title__icontains=keyword)
        if file_type:
            files_qs = files_qs.filter(file_type=file_type)

        context['files'] = list(files_qs)
        context['is_paginated'] = False
        context['page_obj'] = None
        context['search_keyword'] = keyword
        context['search_file_type'] = file_type
        context['file_type_choices'] = UploadedFile.FILE_TYPES

        return context

class DashboardMainView(TemplateView):
    template_name = 'dashboard/dashboard-main.html'

class DashboardPostedJobsView(TemplateView):
    template_name = 'dashboard/dashboard-posted-jobs.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            from files.models import Download
            context['downloaded_files'] = [d.file for d in Download.objects.filter(user=user).select_related('file')]
        else:
            context['downloaded_files'] = []
        return context

class DashboardPostedApplicantsView(TemplateView):
    template_name = 'dashboard/dashboard-posted-applicants.html'

class DashboardSettingsView(TemplateView):
    template_name = 'dashboard/dashboard-settings.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseForbidden('شما اجازه دسترسی به این صفحه را ندارید.')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseForbidden('شما اجازه دسترسی به این صفحه را ندارید.')
        
        # افزودن دسته جدید
        if 'add_category' in request.POST:
            new_cat = request.POST.get('new_category')
            if new_cat:
                Category.objects.create(name=new_cat)
                messages.success(request, 'دسته جدید با موفقیت اضافه شد.')
            return redirect('core:dashboard_settings')

        # افزودن محصول جدید
        form_data = request.POST
        file_obj = request.FILES.get('file')
        file_size = file_obj.size if file_obj else None
        file_type = form_data.get('file_type')
        if file_type == 'PDF':
            file_type = 'pdf'
        elif file_type == 'Word':
            file_type = 'word'
        elif file_type == 'Excel':
            file_type = 'excel'
        elif file_type == 'سایر':
            file_type = 'other'
        is_free = form_data.get('is_free') == 'on'
        price = 0 if is_free else form_data.get('price')
        
        # ایجاد slug برای محصول جدید
        title = form_data.get('title')
        base_slug = slugify(title)
        slug = base_slug
        counter = 1
        while UploadedFile.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
            
        try:
            file = UploadedFile.objects.create(
                title=title,
                file_type=file_type,
                category_id=form_data.get('category'),
                project_manager=str(form_data.get('project_manager')),
                price=price,
                description=form_data.get('description'),
                file=file_obj,
                file_size=file_size,
                is_free=is_free,
                slug=slug,
            )
            messages.success(request, 'محصول جدید با موفقیت اضافه شد.')
            return redirect('core:dashboard_settings')
        except Exception as e:
            messages.error(request, f'خطا در ثبت محصول: {str(e)}')
        return self.render_to_response(self.get_context_data())

@method_decorator(login_required, name='dispatch')
class FileDownloadView(TemplateView):
    def get(self, request, slug):
        file_obj = get_object_or_404(UploadedFile, slug=slug)
        # ثبت دانلود فقط اگر قبلاً ثبت نشده باشد
        Download.objects.get_or_create(user=request.user, file=file_obj)
        response = FileResponse(file_obj.file.open('rb'), as_attachment=True, filename=file_obj.file.name.split('/')[-1])
        return response

class FAQView(TemplateView):
    template_name = 'core/faq.html'

@login_required
def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if name and email and subject and message:
            ContactMessage.objects.create(
                user=request.user,
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            messages.success(request, 'پیام شما با موفقیت ارسال شد.')
            return redirect('core:contact')
        else:
            messages.error(request, 'لطفاً تمام فیلدها را پر کنید.')
    
    return render(request, 'core/contact.html')

class AboutView(TemplateView):
    template_name = 'core/about.html'

def download_file(request, slug):
    file = get_object_or_404(UploadedFile, slug=slug)
    
    # چک کردن وجود فایل فیزیکی
    if not file.file:
        messages.error(request, 'فایل مورد نظر در سرور موجود نیست.')
        return redirect('core:job-details', slug=slug)
        
    try:
        if file.is_free:
            response = FileResponse(file.file.open('rb'), as_attachment=True, filename=file.file.name.split('/')[-1])
            return response
        elif request.user.is_authenticated:
            if request.user.is_staff or file.purchased_by.filter(id=request.user.id).exists():
                # ثبت دانلود فقط اگر قبلاً ثبت نشده باشد
                Download.objects.get_or_create(user=request.user, file=file)
                response = FileResponse(file.file.open('rb'), as_attachment=True, filename=file.file.name.split('/')[-1])
                return response
            else:
                messages.error(request, 'شما باید این فایل را خریداری کنید.')
                return redirect('core:job-details', slug=slug)
        else:
            messages.error(request, 'برای دانلود این فایل باید وارد حساب کاربری خود شوید.')
            return redirect('core:job-details', slug=slug)
    except Exception as e:
        messages.error(request, 'خطا در دانلود فایل. لطفاً با پشتیبانی تماس بگیرید.')
        return redirect('core:job-details', slug=slug)
