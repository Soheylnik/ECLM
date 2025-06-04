from django.views.generic import TemplateView
from django.shortcuts import render, redirect, get_object_or_404
from files.models import UploadedFile, Download
from django.views.generic.detail import DetailView
from django.core.paginator import Paginator
from django.utils.text import slugify
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from files.forms import UploadedFileForm

class HomeView(TemplateView):
    template_name = 'core/home.html'
    def get(self, request):
        return render(request, self.template_name)

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
        # Ensure all files have a slug (auto-generate if missing)
        for f in UploadedFile.objects.all():
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
        # city = request.GET.get('city', '').strip()  # Uncomment if city is added
        if keyword:
            files_qs = files_qs.filter(title__icontains=keyword)
        if file_type:
            files_qs = files_qs.filter(file_type=file_type)
        # if city:
        #     files_qs = files_qs.filter(city__icontains=city)
        files_with_slug = files_qs.exclude(slug='')
        context['files'] = list(files_with_slug)
        context['is_paginated'] = False
        context['page_obj'] = None
        context['search_keyword'] = keyword
        context['search_file_type'] = file_type
        # context['search_city'] = city  # Uncomment if city is added
        # For file_type dropdown
        context['file_type_choices'] = UploadedFile.FILE_TYPES
        # Debug: Print all files with their id, title, and slug
        print("\n--- UploadedFile List (id, title, slug) ---")
        for f in UploadedFile.objects.all():
            print(f.id, f.title, f.slug)
        print("--- END ---\n")
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
        context['product_form'] = UploadedFileForm()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseForbidden('شما اجازه دسترسی به این صفحه را ندارید.')
        form = UploadedFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            from django.contrib import messages
            messages.success(request, 'محصول جدید با موفقیت اضافه شد.')
            return redirect('core:dashboard_settings')
        context = self.get_context_data()
        context['product_form'] = form
        return self.render_to_response(context)

@method_decorator(login_required, name='dispatch')
class FileDownloadView(TemplateView):
    def get(self, request, slug):
        file_obj = get_object_or_404(UploadedFile, slug=slug)
        # ثبت دانلود فقط اگر قبلاً ثبت نشده باشد
        Download.objects.get_or_create(user=request.user, file=file_obj)
        response = FileResponse(file_obj.file.open('rb'), as_attachment=True, filename=file_obj.file.name.split('/')[-1])
        return response
