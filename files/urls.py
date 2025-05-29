from django.urls import path
from .views import FileListView, FileDetailView

app_name = 'files'

urlpatterns = [
    path('', FileListView.as_view(), name='file-list'),
    path('<int:pk>/', FileDetailView.as_view(), name='file-detail'),
]
