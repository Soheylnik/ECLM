
from django.urls import path
from . import views
app_name = 'accounts'

urlpatterns = [ 
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]