from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static
from .views import JournalEntriesView, PictureUploadView, TodoFeed, SendFriendRequestView,\
     AcceptFriendRequestView, RejectFriendRequestView, CreateVouch, MilestoneView, ProjectView, \
    TagSearchView, JournalCommentListView,NewPondertNotificationView, ProjectNotificationsView, LetDownsNotificationsView, \
    VouchedNotificationsView, NotificationsViews, CreateFollow, SearchResultsView, PondView, IndividualPondView, \
    NewPondEntryView, AddToPond, PondRequestView, AcceptPondRequest, DenyPondRequest, \
    NewPondRequestNotificationView, GetNotification,  EditPictureSetView, DeletePictureSet, \
    FailedProjectNotificationView, FailedMilestonesNotificationView, EditIndividualPondView, EditPondView

from .api_view import ApiNewPondEntryView, ApiPictureUploadView, ApiCreateImpressed, \
    ApiEditIndividualPondView, ApiEditPictureSetView, ApiEditPondView, ApiTodoFeed, ApiCreateFollow, ApiCreateVouch, \
    ApiMilestoneView, ApiProjectView, ApiMilestoneSeenCounter, ApiProjectSeenCounter, ApiGetPondList, ApiGetPond, \
    ApiPondRequestView, ApiGetSearchResult, ApiAddToPond, ApiDenyPondRequest, ApiNotificationView, ApiAcceptPondRequest,\
    ApiGetNotification, ApiFriendRequestView, ApiFriendAcceptRequestView, ApiFriendRejectRequestView,\
    ApiHighlightImpressed, ApiRecentUploadImpressed, ApiFindProjectView, ApiFindFriendView,  ApiAllFriendsView,\
    ApiRecentUploadView, ApiSeenRecentUploadCounter,  ApiSeenHighlightCounter, ApiRemoveFriendView, \
    ApiRejectChallengeView, ApiAcceptChallengeView, ApiGetDiscover

urlpatterns = [
    url(r'^journal-feed/$', JournalEntriesView.as_view(), name='journal_entries'),
    url(r'^pic-upload/$', PictureUploadView.as_view(), name='upload_picture'),
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
    url(r'discover-result/$', ApiGetDiscover.as_view(), name="discover_everything"),

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
    url(r'^failed-milestones/$', FailedMilestonesNotificationView.as_view(), name="failed_milestone_notification"),
    
    url(r'^all-ponds/$', PondView.as_view(), name="all_pond"),
    url(r'^pond/(?P<slug>[-\w\d\ ]+)/$', IndividualPondView.as_view(), name="individual_pond"),
    url(r'^pond-entry/$', NewPondEntryView.as_view(), name="new_pond_entry"),
    url(r'^add-to-pond/$', AddToPond.as_view(), name="add_to_pond"),

    url(r'^edit-photo-set/$', EditPictureSetView.as_view(), name="edit_picture_sets"),
    url(r'^delete-picture-set/$', DeletePictureSet.as_view(), name="delete_picture"),
    url(r'^edit-pond-view/$', EditPondView.as_view(), name="edit_pond"),
    url(r'^pond-edit-view/(?P<slug>[-\w\d\ ]+)/$', EditIndividualPondView.as_view(), name="indi_edit_pond"),

    ######################### App Api Calls

    url(r'^api/new-pond-entry/$', ApiNewPondEntryView.as_view(), name="api_new_pond_entry"),
    url(r'^api/new-picture-entry/$', ApiPictureUploadView.as_view(), name="new_picture_entry"),
    url(r'^api/new-video-entry', ApiRecentUploadView.as_view(), name="new_video_entry"),
    url(r'^api/picture-set-edit', ApiEditPictureSetView.as_view(), name="api_picture_set_edit"),
    url(r'^api/individual-pond', ApiEditIndividualPondView.as_view(), name="api_edit_individual_view"),
    url(r'^api/news-feed', ApiTodoFeed.as_view(), name="api_to_do_view"),
    url(r'^api/create-follow', ApiCreateFollow.as_view(), name="api_create_follow"),
    url(r'^api/create-vouch', ApiCreateVouch.as_view(), name="api_createe_vouch"),
    url(r'^api/individual-milestone', ApiMilestoneView.as_view(), name="api_individual__milestone_view"),
    url(r'^api/individual-project', ApiProjectView.as_view(), name="api_individual_project_view"),
    url(r'^api/create-milestone-seen-count', ApiMilestoneSeenCounter.as_view(), name="api_milestone_seen_view"),
    url(r'^api/create-project-seen-count', ApiProjectSeenCounter.as_view(), name="api_project_seen_view"),
    url(r'^api/get-ponds-data', ApiGetPondList.as_view(), name="api_pond_list"),
    url(r'^api/get-pond-data', ApiGetPond.as_view(), name="api_pond"),
    url(r'^api/pond-request', ApiPondRequestView.as_view(), name="api_pond_request_view"),
    url(r'^api/get-search-results', ApiGetSearchResult.as_view(), name="api_search_result"),
    url(r'^api/add-user-to-pond', ApiAddToPond.as_view(), name="api_add_to_pond_view"),
    url(r'^api/deny-user-from-pond', ApiDenyPondRequest.as_view(), name="api_add_to_pond_view"),
    url(r'^api/get-notification', ApiNotificationView.as_view(), name="api_add_to_pond_view"),
    url(r'^api/accept-user-pond-request', ApiAcceptPondRequest.as_view(), name="api_accept_pond_request"),
    url(r'^api/pond-edit/', ApiEditPondView.as_view(), name="api_delete_pond"),
    url(r'^api/notification-status', ApiGetNotification.as_view(), name="api_notification_view"),
    url(r'^api/new-impression', ApiCreateImpressed.as_view(), name="api_new_impression"),
    url(r'api/add-user-to-friends',  ApiFriendRequestView.as_view(), name='api_friend_request'),
    url(r'api/accept-friend-request',  ApiFriendAcceptRequestView.as_view(), name='api_friend_accept_request'),
    url(r'api/deny-friend-request',  ApiFriendRejectRequestView.as_view(), name='api_friend_accept_request'),
    url(r'api/get-friend-request',  ApiFriendRequestView.as_view(), name='api_get_accept_request'),
    url(r'api/new-recent-upload-impression',  ApiRecentUploadImpressed.as_view(), name='api_recent_upload_impressed'),
    url(r'api/new-highlight-impression',  ApiHighlightImpressed.as_view(), name='api_highlight_impressed'),
    url(r'api/get-projects', ApiFindProjectView.as_view(), name='api_find_project'),
    url(r'api/get-friends', ApiFindFriendView.as_view(), name='api_find_friend'),
    url(r'api/get-all-friends', ApiAllFriendsView.as_view(), name='api_all_friends'),
    url(r'api/recent-upload-count', ApiSeenRecentUploadCounter.as_view(), name='api_recent_upload_seen'),
    url(r'api/highlight-upload-count', ApiSeenHighlightCounter.as_view(), name='api_highlight_seen'),
    url(r'api/remove-friend', ApiRemoveFriendView.as_view(), name="api_remove_friend"),
    url(r'api/accept-challenge-request', ApiAcceptChallengeView.as_view(), name="api_accept_challenge"),
    url(r'api/reject-challenge-request', ApiRejectChallengeView.as_view(), name="api_reject_challenge"),
]


urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)