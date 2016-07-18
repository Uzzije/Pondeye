from django.contrib import admin
from image_cropping import ImageCroppingMixin
from models import TikedgeUser, Tasks, UserProject
# Register your models here.

class MyModelAdmin(ImageCroppingMixin, admin.ModelAdmin):
    pass

admin.site.register(TikedgeUser)
admin.site.register(Tasks)
admin.site.register(UserProject)