from django.contrib import admin
from models import Follow, SeenMilestone, ProfilePictures, Notification, PictureSet, VoucheMilestone, \
	Picture, JournalPost, JournalComment, Pond, PondRequest, PondMembership, PondSpecificProject, SeenProject, \
	LetDownMilestone, ProgressPicture, ProgressPictureSet, SeenProgress, SeenPictureSet, WorkEthicRank, LetDownProject, \
	VoucheProject

# Register your models here.

admin.site.register(Follow)
admin.site.register(SeenMilestone)
admin.site.register(ProfilePictures)
admin.site.register(Notification)
admin.site.register(PictureSet)
admin.site.register(VoucheMilestone)
admin.site.register(Picture)
admin.site.register(JournalPost)
admin.site.register(JournalComment)
admin.site.register(Pond)
admin.site.register(PondRequest)
admin.site.register(PondMembership)
admin.site.register(PondSpecificProject)
admin.site.register(SeenProject)
admin.site.register(LetDownMilestone)
admin.site.register(ProgressPicture)
admin.site.register(ProgressPictureSet)
admin.site.register(SeenPictureSet)
admin.site.register(SeenProgress)
admin.site.register(LetDownProject)
admin.site.register(WorkEthicRank)
admin.site.register(VoucheProject)