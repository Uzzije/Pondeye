from django.contrib import admin
from image_cropping import ImageCroppingMixin
from models import TikedgeUser, UserProject, Milestone, TagNames, LaunchEmail
# Register your models here.


class MyModelAdmin(ImageCroppingMixin, admin.ModelAdmin):
    pass

admin.site.register(TikedgeUser)
admin.site.register(UserProject)
admin.site.register(Milestone)
admin.site.register(TagNames)
admin.site.register(LaunchEmail)