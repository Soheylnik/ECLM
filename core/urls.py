from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('faq/', views.FAQView.as_view(), name='faq'),
    path('search-grid/', views.SearchGridView.as_view(), name='search-grid'),
    path('job-details/<slug:slug>/', views.JobDetailsView.as_view(), name='job-details'),
    path('download/<slug:slug>/', views.download_file, name='download_file'),
    path('dashboard/main/', views.DashboardMainView.as_view(), name='dashboard-main'),
    path('dashboard/posted-jobs/', views.DashboardPostedJobsView.as_view(), name='dashboard-posted-jobs'),
    path('dashboard/posted-applicants/', views.DashboardPostedApplicantsView.as_view(), name='dashboard-posted-applicants'),
    path('dashboard/settings/', views.DashboardSettingsView.as_view(), name='dashboard-settings'),
]
