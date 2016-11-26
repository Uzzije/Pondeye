from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static
from .views import JournalEntriesView, PictureUploadView, HomeActivityView, TodoFeed, SendFriendRequestView,\
    FriendRequestView, AcceptFriendRequestView, RejectFriendRequestView, CreateVouch, MilestoneView, ProjectView, \
    TagSearchView, JournalCommentListView, NewFriendNotificationsView, ProjectNotificationsView, LetDownsNotificationsView, \
    VouchedNotificationsView, NotificationsViews, CreateFollowView, SearchResultsView, PondView

urlpatterns = [
    url(r'^journal-feed/$', JournalEntriesView.as_view(), name='journal_entries'),
    url(r'^pic-upload/$', PictureUploadView.as_view(), name='upload_picture'),
    url(r'^activity/$', HomeActivityView.as_view(), name='home_activity'),
    url(r'^feed/$', TodoFeed.as_view(), name="todo_feed"),


    url(r'^send-friend-request/$', SendFriendRequestView.as_view(), name="send_friend_request"),
    url(r'^friend-request/$', FriendRequestView.as_view(), name="friend_request_notifications"),
    url(r'^accept-friend-request/$', AcceptFriendRequestView.as_view(), name="accept_friend_request"),
    url(r'^deny-friend-request/$', RejectFriendRequestView.as_view(), name="reject_friend_request"),
    url(r'^create-vouch/$', CreateVouch.as_view(), name="create_vouch"),
    url(r'^create-follow/$', CreateFollowView.as_view(), name="create_follow"),

    url(r'^milestone/(?P<slug>[-\w\d\ ]+)/$', MilestoneView.as_view(), name="milestone_view"),
    url(r'^project/(?P<slug>[-\w\d\ ]+)/$', ProjectView.as_view(), name="project_view"),

    url(r'^tag-search/(?P<word>[-\w\d\ ]+)/$', TagSearchView.as_view(), name="tag_search"),
    url(r'search-results/$', SearchResultsView.as_view(), name="search_everything"),

    url(r'^notifications/$', NotificationsViews.as_view(), name="notifications"),
    url(r'^journal-thoughts/(?P<slug>[-\w\d\ ]+)/$', JournalCommentListView.as_view(), name="journal_post_comments"),
    url(r'^new-friend-notifications/$', NewFriendNotificationsView.as_view(), name="new_friends_notifications"),
    url(r'^project-interest-notifications/$', ProjectNotificationsView.as_view(), name="project_interest_notifications"),
    url(r'^let-downs-notifications/$', LetDownsNotificationsView.as_view(), name="let_downs_notifications"),
    url(r'^vouched-notifications/$', VouchedNotificationsView.as_view(), name="vouch_notifications"),
    url(r'^pond/$', PondView.as_view(), name="all_pond"),

]


urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)