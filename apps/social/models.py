from __future__ import unicode_literals
from django.db import models
from image_cropping import ImageRatioField
from ..tasks.models import TikedgeUser, UserProject, Milestone, TagNames
from friendship.models import FriendshipRequest
from django.contrib.auth.models import User
from django.utils.timezone import now
from global_variables import NEW_PROJECT
from random import randint
# Create your models here.


class ProfilePictures(models.Model):
    image_name = models.CharField(max_length=100)
    profile_pics = models.ImageField(upload_to='image/%Y/%m/%d', verbose_name="profile image")
    cropping = ImageRatioField('profile_pics', '5x5')
    tikedge_user = models.ForeignKey(TikedgeUser, blank=True, null=True)
    date_uploaded =  models.DateTimeField(default=now)


class Picture(models.Model):
    image_name = models.CharField(max_length=300)
    milestone_pics = models.ImageField(upload_to='image/tasks/%Y/%m/%d', verbose_name="profile image")
    cropping = ImageRatioField('milestone_pics', '5x5')
    tikedge_user = models.ForeignKey(TikedgeUser, blank=True, null=True)
    date_uploaded = models.DateTimeField(default=now)
    is_before = models.BooleanField(default=True)

    def __str__(self):
        return '%s %s' % (self.tikedge_user.user.username, self.image_name)


class PictureSet(models.Model):
    before_picture = models.ForeignKey(Picture, blank=True, null=True, related_name="before_picture")
    after_picture = models.ForeignKey(Picture, blank=True, null=True, related_name="after_picture")
    milestone = models.ForeignKey(Milestone, blank=True, null=True)
    tikedge_user = models.ForeignKey(TikedgeUser, blank=True, null=True)

    def __str__(self):
        return '%s' % self.before_picture.image_name


class Friends(models.Model):
    user = models.ForeignKey(TikedgeUser, blank=True, null=True)
    friends = models.ManyToManyField(TikedgeUser, related_name="user_friends")


class SeenMilestone(models.Model):
    users = models.ManyToManyField(TikedgeUser, verbose_name="Users That saw the milestones")
    tasks = models.ForeignKey(Milestone, blank=True, null=True)


class SeenProject(models.Model):
    users = models.ManyToManyField(TikedgeUser, verbose_name="Users That saw the projects")
    tasks = models.ForeignKey(UserProject, blank=True, null=True)


class SeenPictureSet(models.Model):
    users = models.ManyToManyField(TikedgeUser, verbose_name="Users That saw the pictureSet")
    tasks = models.ForeignKey(PictureSet, blank=True, null=True)


class VoucheMilestone(models.Model):
    users = models.ManyToManyField(TikedgeUser, verbose_name="User That Vouche For the milestone")
    tasks = models.ForeignKey(Milestone, blank=True, null=True)


class BuildCredMilestone(models.Model):
    users = models.ManyToManyField(TikedgeUser, verbose_name="User That Milestone Owner Built Cred For")
    tasks = models.ForeignKey(Milestone, blank=True, null=True)


class Follow(models.Model):
    users = models.ManyToManyField(TikedgeUser, verbose_name="users that follow/interested in a project")
    tasks = models.ForeignKey(UserProject, blank=True, null=True)


class LetDownMilestone(models.Model):
    users = models.ManyToManyField(TikedgeUser, verbose_name="users that were let down by vouche for your Milestone")
    tasks = models.ForeignKey(Milestone, blank=True, null=True)


class Notification(models.Model):
    friend_request = models.ForeignKey(FriendshipRequest, blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True)
    type_of_notification = models.CharField(max_length=100)
    created = models.DateTimeField(default=now)
    read = models.BooleanField(default=False)
    project_update = models.ForeignKey(UserProject, blank=True, null=True)
    name_of_notification = models.CharField(max_length=300, default="")

    def __str__(self):
        return self.name_of_notification


class JournalPost(models.Model):
    entry_blurb = models.CharField(default=None, max_length=240)
    day_entry = models.IntegerField(default=1)
    day_created = models.DateTimeField(default=now)
    event_type = models.CharField(default=NEW_PROJECT, max_length=20)
    picture_set_entry = models.ForeignKey(PictureSet, null=True)
    milestone_entry = models.ForeignKey(Milestone, null=True)
    new_project_entry = models.ForeignKey(UserProject, null=True)
    user = models.ForeignKey(TikedgeUser, null=True)
    is_deleted = models.BooleanField(default=False)
    is_picture_set = models.BooleanField(default=False)
    is_milestone_entry = models.BooleanField(default=False)
    is_project_entry = models.BooleanField(default=False)
    slug = models.SlugField(default=None, max_length=100)

    def save(self, *args, **kwargs):
        if not self.slug:
            str_slug = str(randint(0, 999999))
            str_slug_two = str(randint(9000, 99999999))
            self.slug = str_slug + str_slug_two
        super(JournalPost, self).save(*args, **kwargs)


class JournalComment(models.Model):
    journal_post = models.ForeignKey(JournalPost, null=True)
    comment = models.CharField(max_length=2000, default=None)
    is_deleted = models.BooleanField(default=False)


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


class Pond(models.Model):
    name_of_pond = models.CharField(max_length=250)
    pond_creator = models.ForeignKey(TikedgeUser, null=True, blank=True, related_name='pond_creater')
    pond_members = models.ManyToManyField(TikedgeUser, related_name='pond_member')
    date_created = models.DateTimeField(default=now)
    date_deleted = models.DateTimeField(blank=True, null=True)
    tags = models.ManyToManyField(TagNames)


class PondRequest(models.Model):
    user = models.ForeignKey(TikedgeUser, blank=True, null=True)
    pond = models.ForeignKey(Pond, blank=True, null=True)
    date_requested = models.DateTimeField(default=now)
    date_response = models.DateTimeField(blank=True, null=True)
    request_accepted = models.BooleanField(default=False)
    request_denied = models.BooleanField(default=False)
    request_responded_to = models.BooleanField(default=False)
    member_that_responded = models.ForeignKey(TikedgeUser, blank=True, null=True, related_name='the_member_that_responded')





            







