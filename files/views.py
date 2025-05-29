from django.views.generic import ListView, DetailView
from .models import UploadedFile

class FileListView(ListView):
    model = UploadedFile
    template_name = 'files/file_list.html'
    context_object_name = 'files'

class FileDetailView(DetailView):
    model = UploadedFile
    template_name = 'files/file_detail.html'
    context_object_name = 'file'
