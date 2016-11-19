from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static
from .views import ProfileView, PictureUploadView, HomeActivityView, TodoFeed, PeopleView, SendFriendRequestView,\
    FriendRequestView, AcceptFriendRequestView, RejectFriendRequestView, CreateVouch

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
    url(r'^create-vouch/$', CreateVouch.as_view(), name="create_vouch"),
]


urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)