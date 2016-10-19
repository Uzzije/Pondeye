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
    cropping = ImageRatioField('profile_pics', '5x5')
    tikedge_user = models.ForeignKey(TikedgeUser, blank=True, null=True)
    date_uploaded =  models.DateTimeField(default=now)


class TaskPicture(models.Model):
    image_name = models.CharField(max_length=100)
    task_pics = models.ImageField(upload_to='image/tasks/%Y/%m/%d', verbose_name="profile image")
    cropping = ImageRatioField('task_pics', '5x5')
    tikedge_user = models.ForeignKey(TikedgeUser, blank=True, null=True)
    task = models.ForeignKey(Tasks, blank=True, null=True)
    date_uploaded =  models.DateTimeField(default=now)


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
    picture_post = models.ForeignKey(TaskPicture, blank=True, null=True)
    project_update = models.ForeignKey(UserProject, blank=True, null=True)
    tasks = models.ForeignKey(Tasks, blank=True, null=True)
    name_of_notification = models.CharField(max_length=300, default="")

    def __str__(self):
        return self.name_of_notification


class Graded(models.Model):
    credibility_count = models.IntegerField(default=0)
    consistency_count = models.IntegerField(default=0)
    max_credibility_count = models.IntegerField(default=0)
    max_consistency_count = models.IntegerField(default=0)
    correct_vouch = models.IntegerField(default=0, verbose_name="user vouch for tasks that got done")
    vouch_fail = models.IntegerField(default=0, verbose_name="user vouch for tasks that didn't get done")
    seen_without_vouch_fail = models.IntegerField(default=0, verbose_name="user saw tasks thats that didn't get done, and didn't vouche for it")
    seen_without_vouch_success = models.IntegerField(default=0, verbose_name="user saw a tasks that got completed, but didn't vouche for it")
    failed_tasks = models.IntegerField(default=0)
    completed_tasks = models.IntegerField(default=0)
    user = models.ForeignKey(TikedgeUser, blank=True, null=True)
    prior_crediblity_count = models.IntegerField(default=0)
    prior_consitency_count = models.IntegerField(default=0)

    def get_grade_for_credibility(self):
        credibility_grade = self.get_num_grade_credibility()
        if (credibility_grade >= 0 and credibility_grade <= 59):
            return 'F'
        elif (credibility_grade > 59 and credibility_grade <= 63):
            return 'D-'
        elif (credibility_grade > 63 and credibility_grade <= 66):
            return 'D'
        elif (credibility_grade > 66 and credibility_grade <= 69):
            return 'D+'
        elif (credibility_grade > 69 and credibility_grade <= 73):
            return 'C-'
        elif (credibility_grade > 73 and credibility_grade <= 76):
            return 'C'
        elif (credibility_grade > 76 and credibility_grade <= 79):
            return 'C+'
        elif (credibility_grade > 79 and credibility_grade <= 83):
            return 'B-'
        elif (credibility_grade > 83 and credibility_grade <= 86):
            return 'B'
        elif (credibility_grade > 86 and credibility_grade <= 89):
            return 'B+'
        elif (credibility_grade > 90 and credibility_grade <= 93):
            return 'A-'
        elif (credibility_grade > 93 and credibility_grade <= 96):
            return 'A'
        elif (credibility_grade > 96 and credibility_grade <= 100):
            return 'A+'

    def get_grade_for_consistency(self):
        consitency_grade = self.get_num_grade_consistency()
        if (consitency_grade >= 0 and consitency_grade <= 59):
            return 'F'
        elif (consitency_grade > 59 and consitency_grade <= 63):
            return 'D-'
        elif (consitency_grade > 63 and consitency_grade <= 66):
            return 'D'
        elif (consitency_grade > 66 and consitency_grade <= 69):
            return 'D+'
        elif (consitency_grade > 69 and consitency_grade <= 73):
            return 'C-'
        elif (consitency_grade > 73 and consitency_grade <= 76):
            return 'C'
        elif (consitency_grade > 76 and consitency_grade <= 79):
            return 'C+'
        elif (consitency_grade > 79 and consitency_grade <= 83):
            return 'B-'
        elif (consitency_grade > 83 and consitency_grade <= 86):
            return 'B'
        elif (consitency_grade > 86 and consitency_grade <= 89):
            return 'B+'
        elif (consitency_grade > 90 and consitency_grade <= 93):
            return 'A-'
        elif (consitency_grade > 93 and consitency_grade <= 96):
            return 'A'
        elif (consitency_grade > 96 and consitency_grade <= 100):
            return 'A+'
        
    def get_num_grade_consistency(self):
        ratio = float(self.consistency_count/self.max_consistency_count)*100
        return int(ratio)
    
    def get_num_grade_credibility(self):
        ratio = float(self.credibility_count/self.max_credibility_count)*100
        return int(ratio)
            







