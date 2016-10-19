from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static
from .views import ProfileView, PictureUploadView, HomeActivityView, TodoFeed, PeopleView, SendFriendRequestView,\
    FriendRequestView, AcceptFriendRequestView, RejectFriendRequestView, ApiTodoFeed, ApiCreateFollow, ApiCreateVouch,\
    ApiPeopleView, ApiSendFriendRequestView, ApiFriendRequestView, ApiRejectFriendRequestView, ApiAcceptFriendRequestView,\
    ApiPictureUploadView, ApiAddNewPictureToTask, ApiHomeActivityView, ApiGradeNotifications

urlpatterns = [
    url(r'^profileview/$', ProfileView.as_view(), name='profile_view'),
    url(r'^pic-upload/$', PictureUploadView.as_view(), name='upload_picture'),
    url(r'^activity/$', HomeActivityView.as_view(), name='home_activity'),
    url(r'^feed/$', TodoFeed.as_view(), name="todo_feed"),
    url(r'^find-people/$', PeopleView.as_view(), name="find_people"),
    url(r'^send-friend-request/$', SendFriendRequestView.as_view(), name="send_friend_request"),
    url(r'^friend-request/$', FriendRequestView.as_view(), name="friend_request"),
    url(r'^accept-friend-request/$', AcceptFriendRequestView.as_view(), name="accept_friend_request"),
    url(r'^deny-friend-request/$', RejectFriendRequestView.as_view(), name="reject_friend_request"),
    url(r'^api/newsfeed/$', ApiTodoFeed.as_view(), name='to_do_feed_api'),
    url(r'^api/create-vouch', ApiCreateVouch.as_view(), name='create_vouch_api'),
    url(r'^api/create-follow/$', ApiCreateFollow.as_view(), name='create_follow_api'),
    url(r'^api/social-search/$', ApiPeopleView.as_view(), name='find_people_api'),
    url(r'^api/send-friend-request/$', ApiSendFriendRequestView.as_view(), name='send_request_api'),
    url(r'^api/friend-request/$', ApiFriendRequestView.as_view(), name='friend_request_view_api'),
    url(r'^api/deny-friend-request/$', ApiRejectFriendRequestView.as_view(), name='deny_friend_request_view_api'),
    url(r'^api/accept-friend-request/$', ApiAcceptFriendRequestView.as_view(), name='accept_friend_request_view_api'),
    url(r'^api/upload-pictures/$', ApiPictureUploadView.as_view(), name='upload_pictures'),
    url(r'^api/add-new-pic-to-task', ApiAddNewPictureToTask.as_view(), name="add_pic_to_task"),
    url(r'^api/get-home-activities', ApiHomeActivityView.as_view(), name="get_home_activity_view"),
    url(r'^api/get-grade-notifications', ApiGradeNotifications.as_view(), name="grade-notification-view"),
]


urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)