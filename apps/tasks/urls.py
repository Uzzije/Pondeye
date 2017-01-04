from django.conf.urls import url
from .views import RegisterView, LoginView, HomeView, AddProject, LogoutView,\
        ProfileView, CheckMilestoneDone, \
    CheckFailedProjectMilestoneView, CheckPojectDone, PreLaunchView, ChangePersonalInformationView, MilestoneEditView, \
    ProjectEditView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^home/$', HomeView.as_view(), name='home'),
    url(r'^profile/(?P<slug>[-\w\d\ ]+)$', ProfileView.as_view(), name='profile_view'),
    url(r'^new-tasks/$', AddProject.as_view(), name='add_proj'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^api/milstone-done', CheckMilestoneDone.as_view(), name="milestone_done"),
    url(r'^api/project-done', CheckPojectDone.as_view(), name="project_done"),
    url(r'^api/check-failed', CheckFailedProjectMilestoneView.as_view(), name="check_milestone_proj_failed"),
    url(r'^$', PreLaunchView.as_view(), name='pre_launch_view'),
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^change-personal-info/$', ChangePersonalInformationView.as_view(), name="change_personal_info"),
    url(r'^milestone-edit/$', MilestoneEditView.as_view(), name="milestone_edit"),
    url(r'^project-edit/$', ProjectEditView.as_view(), name="project_edit")
]


urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)