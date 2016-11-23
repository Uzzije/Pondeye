from django.conf.urls import url
from .views import RegisterView, LoginView, HomeView, AddProject, ListOfTasksViews, LogoutView,\
    ApiCheckFailedTask, ApiCheckTaskDone, IndividualTaskView, ProfileView, CheckMilestoneDone, \
    CheckFailedProjectMilestoneView, CheckPojectDone
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^home/$', HomeView.as_view(), name='home'),
    url(r'^profile/(?P<user_name>[-\w\d\ ]+)$', ProfileView.as_view(), name='profile_view'),
    url(r'^new-tasks/$', AddProject.as_view(), name='add_proj'),
    url(r'^list_of_tasks/$', ListOfTasksViews.as_view(), name='list_of_tasks'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^api/task-done-check-off', ApiCheckTaskDone.as_view(), name="task_done"),
    url(r'^api/task-failed-check-off', ApiCheckFailedTask.as_view(), name="task_failed"),
    url(r'^api/individual-view/$', IndividualTaskView.as_view(), name="indiv_task_view"),
    url(r'^api/milstone-done', CheckMilestoneDone.as_view(), name="milestone_done"),
    url(r'^api/project-done', CheckPojectDone.as_view(), name="project_done"),
    url(r'^api/check-failed', CheckFailedProjectMilestoneView.as_view(), name="check_milestone_proj_failed"),
]


urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)