from django.urls import path
from .views import FileListView, FileDetailView

app_name = 'files'

urlpatterns = [
    path('', FileListView.as_view(), name='file-list'),
    path('<slug:slug>/', FileDetailView.as_view(), name='file-detail'),
]
