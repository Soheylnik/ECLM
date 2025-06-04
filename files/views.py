from django.views.generic import ListView, DetailView
from .models import UploadedFile
from django.shortcuts import get_object_or_404

class FileListView(ListView):
    model = UploadedFile
    template_name = 'files/file_list.html'
    context_object_name = 'files'
    # price, project_manager, and file_size are now model fields and available in context

class FileDetailView(DetailView):
    model = UploadedFile
    template_name = 'files/file_detail.html'
    context_object_name = 'file'

    def get_object(self):
        return get_object_or_404(UploadedFile, slug=self.kwargs['slug'])
