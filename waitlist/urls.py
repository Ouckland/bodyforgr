from django.urls import path
from . import views

app_name = "waitlist"

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('signup/', views.waitlist_signup, name='signup'),  # Changed from early_access_signup
    path('thanks/', views.waitlist_success, name='thanks'),
    path('api/signup/', views.waitlist_api_signup, name='api_signup'),
]