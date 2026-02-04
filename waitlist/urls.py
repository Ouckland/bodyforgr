from . import views
from django.urls import path

app_name = "waitlist"

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('early-access-signup/', views.waitlist_signup, name='early_access_signup'),
    path('thanks/', views.waitlist_success, name='thanks'),
]