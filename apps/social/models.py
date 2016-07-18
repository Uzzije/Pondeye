from __future__ import unicode_literals
from django.db import models
from image_cropping import ImageRatioField
from ..tasks.models import TikedgeUser, Tasks, UserProject
from friendship.models import FriendshipRequest
from django.contrib.auth.models import User
from django.utils.timezone import now
# Create your models here.


class ProfilePictures(models.Model):
    image_name = models.CharField(max_length=100)
    profile_pics = models.ImageField(upload_to='image/%Y/%m/%d', verbose_name="profile image")
    cropping = ImageRatioField('profile_pics', '60x60')
    tikede_user = models.ForeignKey(TikedgeUser, blank=True, null=True)


class Friends(models.Model):
    user = models.ForeignKey(TikedgeUser, blank=True, null=True)
    friends = models.ManyToManyField(TikedgeUser, related_name="user_friends")


class Seen(models.Model):
    users = models.ManyToManyField(TikedgeUser, verbose_name="Users That saw the tasks")
    tasks = models.ForeignKey(Tasks, blank=True, null=True)


class Vouche(models.Model):
    users = models.ManyToManyField(TikedgeUser, verbose_name="User That Vouche For the Task")
    tasks = models.ForeignKey(Tasks, blank=True, null=True)


class BuildCred(models.Model):
    users = models.ManyToManyField(TikedgeUser, verbose_name="User That Tasks Owner Built Cred For")
    tasks = models.ForeignKey(Tasks, blank=True, null=True)


class Follow(models.Model):
    users = models.ManyToManyField(TikedgeUser, verbose_name="users that follow a project")
    tasks = models.ForeignKey(UserProject, blank=True, null=True)


class LetDown(models.Model):
    users = models.ManyToManyField(TikedgeUser, verbose_name="users that were let down by vouche for your task")
    tasks = models.ForeignKey(Tasks, blank=True, null=True)


class Notification(models.Model):
    friend_request = models.ForeignKey(FriendshipRequest, blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True)
    type_of_notification = models.CharField(max_length=100)
    created = models.DateTimeField(default=now)
    read = models.BooleanField(default=False)