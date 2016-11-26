from django.contrib import admin
from models import Follow, SeenMilestone, ProfilePictures, Graded, Notification, PictureSet, VoucheMilestone, \
	Picture, JournalPost, JournalComment
# Register your models here.

admin.site.register(Follow)
admin.site.register(SeenMilestone)
admin.site.register(ProfilePictures)
admin.site.register(Graded)
admin.site.register(Notification)
admin.site.register(PictureSet)
admin.site.register(VoucheMilestone)
admin.site.register(Picture)
admin.site.register(JournalPost)
admin.site.register(JournalComment)