
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),       
    path('', include('core.urls')),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header= 'Congregação Cristã do Brasil' 
admin.site.site_title='Obra da Piedade de Franca'
admin.site.index_title='CDA - Controle de Doações de Alimentos'

