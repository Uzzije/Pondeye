from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static
from .views import JournalEntriesView, PictureUploadView, HomeActivityView, TodoFeed, SendFriendRequestView,\
    FriendRequestView, AcceptFriendRequestView, RejectFriendRequestView, CreateVouch, MilestoneView, ProjectView, \
    TagSearchView, JournalCommentListView,NewPondertNotificationView, ProjectNotificationsView, LetDownsNotificationsView, \
    VouchedNotificationsView, NotificationsViews, CreateFollow, SearchResultsView, PondView, IndividualPondView, \
    NewPondEntryView, AddToPond, PondRequestView, AcceptPondRequest, DenyPondRequest, \
    NewPondRequestNotificationView, GetNotification

urlpatterns = [
    url(r'^journal-feed/$', JournalEntriesView.as_view(), name='journal_entries'),
    url(r'^pic-upload/$', PictureUploadView.as_view(), name='upload_picture'),
    url(r'^activity/$', HomeActivityView.as_view(), name='home_activity'),
    url(r'^feed/$', TodoFeed.as_view(), name="todo_feed"),

    url(r'^send-friend-request/$', SendFriendRequestView.as_view(), name="send_friend_request"),
    url(r'^accept-friend-request/$', AcceptFriendRequestView.as_view(), name="accept_friend_request"),
    url(r'^deny-friend-request/$', RejectFriendRequestView.as_view(), name="reject_friend_request"),

    url(r'^create-vouch/$', CreateVouch.as_view(), name="create_vouch"),
    url(r'^create-follow/$', CreateFollow.as_view(), name="create_follow"),
    url(r'^milestone/(?P<slug>[-\w\d\ ]+)/$', MilestoneView.as_view(), name="milestone_view"),
    url(r'^project/(?P<slug>[-\w\d\ ]+)/$', ProjectView.as_view(), name="project_view"),

    url(r'^tag-search/(?P<word>[-\w\d\ ]+)/$', TagSearchView.as_view(), name="tag_search"),
    url(r'search-results/$', SearchResultsView.as_view(), name="search_everything"),

    url(r'^notifications/$', NotificationsViews.as_view(), name="notifications"),
    url(r'^journal-thoughts/(?P<slug>[-\w\d\ ]+)/$', JournalCommentListView.as_view(), name="journal_post_comments"),
    url(r'^new-ponder-notifications/$', NewPondertNotificationView.as_view(), name="new_ponder_notifications"),
    url(r'^project-interest-notifications/$', ProjectNotificationsView.as_view(), name="project_interest_notifications"),
    url(r'^let-downs-notifications/$', LetDownsNotificationsView.as_view(), name="let_downs_notifications"),
    url(r'^vouched-notifications/$', VouchedNotificationsView.as_view(), name="vouch_notifications"),
        url(r'^pond-join-request/$', PondRequestView.as_view(), name="pond_join_request"),
    url(r'^pond-deny-request/$', DenyPondRequest.as_view(), name="deny_from_pond_notification"),
    url(r'^pond-request/$', AcceptPondRequest.as_view(), name="pond_request_notifications"),
    url(r'^new-ponder-request/$', NewPondRequestNotificationView.as_view(), name="new_ponder_request_notifications"),
    url(r'^get-notification/$', GetNotification.as_view(), name="get_main_notifications"),

    
    url(r'^all-ponds/$', PondView.as_view(), name="all_pond"),
    url(r'^pond/(?P<slug>[-\w\d\ ]+)/$', IndividualPondView.as_view(), name="individual_pond"),
    url(r'^pond-entry/$', NewPondEntryView.as_view(), name="new_pond_entry"),
    url(r'^add-to-pond/$', AddToPond.as_view(), name="add_to_pond"),

]


urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)