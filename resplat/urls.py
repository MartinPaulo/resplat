"""resplat URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic import RedirectView

from resplat import views

admin.site.site_title = 'UoM Storage'  # ordinarily 'Django Administration'
admin.site.site_header = 'UoM Storage Management'  # 'Django Administration'
admin.site.index_title = 'Administration'  # ordinarily 'Site administration'

urlpatterns = [
    url(r'^resplat/doc/', include('django.contrib.admindocs.urls')),
    url(r'^resplat/', admin.site.urls),
    url(r'^resplat/stats/', include('storage.urls')),
    url(r'^$', views.index, name='index'),
    # from http://staticfiles.productiondjango.com/blog/failproof-favicons/
    url(r'^favicon.ico$', RedirectView.as_view(
        url=staticfiles_storage.url('favicon.ico'),
        permanent=False), name="favicon")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

