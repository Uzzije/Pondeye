from django.conf.urls import url
from .views import RegisterView, LoginView, HomeView, AddProject, LogoutView,\
        ProfileView, CheckMilestoneDone, \
    CheckFailedProjectMilestoneView, CheckPojectDone, PreLaunchView, ChangePersonalInformationView, MilestoneEditView, \
    ProjectEditView
from .api_view import ApiLoginView, ApiRegistrationView, ApiGetPostInfo, \
    ApiNewMilestone, ApiProjectEditView, ApiMilestoneEditView, ApiChangePersonalInformationView, ApiProfileView,\
    ApiProfilePictureView, ApiCheckMilestoneDone, ApiCheckProjectDone, ApiCheckFailedProjectMilestoneView, \
    ApiPasswordResetView, ApiSendResetPasswordCode,  ApiRunRanking, ApiNewChallenge, ApiAllChallengeView, \
    ApiAllChallengeRequestView
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
    url(r'^project-edit/$', ProjectEditView.as_view(), name="project_edit"),

    ######################## api

    url(r'^api/login/$', ApiLoginView.as_view(), name="api_login"),
    url(r'^api/register', ApiRegistrationView.as_view(), name="api_register"),
    url(r'^api/get-new-post-info', ApiGetPostInfo.as_view(), name="api_post_info"),
    url(r'^api/create-new-milestone', ApiNewMilestone.as_view(), name="api_create_new_milestone"),
    url(r'^api/project-edit', ApiProjectEditView.as_view(), name="api_project_edit"),
    url(r'^api/milestone-edit', ApiMilestoneEditView.as_view(), name="api_milestone_edit"),
    url(r'^api/personal-info-edit', ApiChangePersonalInformationView.as_view(), name="api_personal_info_edit"),
    url(r'^api/profile-view', ApiProfileView.as_view(), name="api_profile_view"),
    url(r'^api/add-profile-picture', ApiProfilePictureView.as_view(), name="api_add_profile_picture"),
    url(r'^api/milestone-marked-done', ApiCheckMilestoneDone.as_view(), name="api_milestone_done"),
    url(r'^api/project-marked-done', ApiCheckProjectDone.as_view(), name="api_project_done"),
    url(r'^api/check-proj-and-mil-failed', ApiCheckFailedProjectMilestoneView.as_view(), name="api_check_milestone_proj_failed"),
    url(r'^api/send-reset-pass-code', ApiSendResetPasswordCode.as_view(), name="api_pass_reset_code"),
    url(r'^api/reset-password', ApiPasswordResetView.as_view(), name="api_pass_reset_view"),
    url(r'^api/rank-all-users', ApiRunRanking.as_view(), name='api_run_ranking_algorithm'),
    url(r'^api/create-new-challenge', ApiNewChallenge.as_view(), name='api_create_challenge'),
    url(r'api/get-all-challenge/$', ApiAllChallengeView.as_view(), name='api_all_challenge'),
    url(r'api/challenge-request', ApiAllChallengeRequestView.as_view(), name='api_all_challenge_request'),

]


urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)