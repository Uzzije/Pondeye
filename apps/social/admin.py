from django.contrib import admin
from models import FollowChallenge, Notification, \
	Pond, PondRequest, PondMembership, PondSpecificProject,\
	PondProgressFeed, ShoutOutEmailAndNumber, ProgressVideo, ProgressVideoSet,\
	SeenChallenge, SeenRecentUpload, SeenVideoSet, CommentRecentUploads, Challenge, ChallengeRating, \
	ChallengeVideo, CommentChallengeAcceptance, CommentRequestFeed, CommentVideoCelebrations

# Register your models here.

admin.site.register(SeenChallenge)
admin.site.register(SeenRecentUpload)
admin.site.register(SeenVideoSet)
admin.site.register(Notification)
admin.site.register(CommentRecentUploads)
admin.site.register(Challenge)
admin.site.register(ChallengeRating)
admin.site.register(ChallengeVideo)
admin.site.register(CommentChallengeAcceptance)
admin.site.register(Pond)
admin.site.register(PondRequest)
admin.site.register(PondMembership)
admin.site.register(PondSpecificProject)
admin.site.register(CommentRequestFeed)
admin.site.register(CommentVideoCelebrations)
admin.site.register(PondProgressFeed)
admin.site.register(ShoutOutEmailAndNumber)
admin.site.register(ProgressVideo)
admin.site.register(ProgressVideoSet)
admin.site.register(FollowChallenge)