from django.urls import path, include, re_path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    re_path(r'^$', RedirectView.as_view(url='/admin/', permanent=True)),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
