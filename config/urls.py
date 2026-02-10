# bodyforgr/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('waitlist/', include('waitlist.urls')),  # This includes your waitlist app
    path('', RedirectView.as_view(url='/waitlist/', permanent=False)),  # Redirect root to waitlist
]

# Serve static files in development
if settings.DEBUG:
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler404 = 'waitlist.views.custom_404'
handler500 = 'waitlist.views.custom_500'