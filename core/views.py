from django.views.generic import TemplateView
from django.shortcuts import render, redirect
class HomeView(TemplateView):
    template_name = 'core/home.html'
    def get(self, request):
        return render(request, self.template_name)
class ContactView(TemplateView):
    template_name = 'contact/contact.html'
    def get(self, request):
        return render(request, self.template_name)
class JobDetailsView(TemplateView):
    template_name = 'core/jobdetails.html'

class SearchGridView(TemplateView):
    template_name = 'core/search-grid.html'

class DashboardMainView(TemplateView):
    template_name = 'dashboard/dashboard-main.html'

class DashboardPostedJobsView(TemplateView):
    template_name = 'dashboard/dashboard-posted-jobs.html'

class DashboardPostedApplicantsView(TemplateView):
    template_name = 'dashboard/dashboard-posted-applicants.html'

class DashboardSettingsView(TemplateView):
    template_name = 'dashboard/dashboard-settings.html'
