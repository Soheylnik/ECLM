from django.urls import path
from .views import *

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('job-details/', JobDetailsView.as_view(), name='jobdetails'),
    path('search/', SearchGridView.as_view(), name='search'),

    # Dashboard
    path('dashboard/', DashboardMainView.as_view(), name='dashboard_main'),
    path('dashboard/posted-jobs/', DashboardPostedJobsView.as_view(), name='dashboard_posted_jobs'),
    path('dashboard/posted-applicants/', DashboardPostedApplicantsView.as_view(), name='dashboard_posted_applicants'),
    path('dashboard/settings/', DashboardSettingsView.as_view(), name='dashboard_settings'),
]
