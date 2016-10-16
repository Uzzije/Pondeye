from django.contrib import admin
from image_cropping import ImageCroppingMixin
from models import TikedgeUser, Tasks, UserProject, PendingTasks
# Register your models here.

class MyModelAdmin(ImageCroppingMixin, admin.ModelAdmin):
    pass

admin.site.register(TikedgeUser)
admin.site.register(Tasks)
admin.site.register(UserProject)
admin.site.register(PendingTasks)