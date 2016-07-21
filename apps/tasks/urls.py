from django.conf.urls import url
from .views import RegisterView, LoginView, HomeView, AddTasks, ListOfTasksViews, LogoutView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^home/$', HomeView.as_view(), name='home'),
    url(r'^new-tasks/$', AddTasks.as_view(), name='add_task'),
    url(r'^list_of_tasks/$', ListOfTasksViews.as_view(), name='list_of_tasks'),
    url(r'^logout/$', LogoutView.as_view(), name='logout')
]


urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)