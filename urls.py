"""tikedge URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static
import notifications.urls

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('apps.tasks.urls', namespace='tasks')),
    url(r'^social/', include('apps.social.urls', namespace='social')),
    url(r'^calendar/', include('django_bootstrap_calendar.urls', namespace="django_bootstrap_calendar")),
    url('^inbox/notifications/', include(notifications.urls, namespace='notifications')),
    url(r'^friendship/', include('friendship.urls'))
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)