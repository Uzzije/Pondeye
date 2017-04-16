from __future__ import unicode_literals
from django.db import models
from image_cropping import ImageRatioField
from ..tasks.models import TikedgeUser, UserProject, Milestone, TagNames
from friendship.models import FriendshipRequest
from django.contrib.auth.models import User
from django.utils.timezone import now
from global_variables import PROJECT
from random import randint
from django.template.defaultfilters import slugify


class ProfilePictures(models.Model):
    image_name = models.CharField(max_length=100)
    profile_pics = models.ImageField(upload_to='image/%Y/%m/%d', verbose_name="profile image")
    cropping = ImageRatioField('profile_pics', '5x5')
    tikedge_user = models.ForeignKey(TikedgeUser, blank=True, null=True)
    date_uploaded =  models.DateTimeField(default=now)
    is_deleted = models.BooleanField(default=False)


class Picture(models.Model):
    image_name = models.CharField(max_length=300)
    milestone_pics = models.ImageField(upload_to='image/tasks/%Y/%m/%d', verbose_name="profile image")
    cropping = ImageRatioField('milestone_pics', '5x5')
    tikedge_user = models.ForeignKey(TikedgeUser, blank=True, null=True)
    date_uploaded = models.DateTimeField(default=now)
    last_edited = models.DateTimeField(null=True, blank=True)
    is_before = models.BooleanField(default=True)

    def __str__(self):
        return '%s %s' % (self.tikedge_user.user.username, self.image_name)


class ProjectPicture(models.Model):
    image_name = models.CharField(max_length=300)
    date_uploaded = models.DateTimeField(default=now)
    last_edited = models.DateTimeField(null=True, blank=True)
    is_before = models.BooleanField(default=True)
    picture = models.ImageField(upload_to='image/tasks/%Y/%m/%d', verbose_name="profile image")
    is_deleted = models.BooleanField(default=False)
    project = models.ForeignKey(UserProject, blank=True, null=True)

    def __str__(self):
        return self.project.name_of_project


class ProgressPicture(models.Model):
    image_name = models.TextField(max_length=600)
    picture = models.ImageField(upload_to='image/progresspicture/%Y/%m/%d', verbose_name="progress image")
    name_of_progress = models.TextField(max_length=600, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    last_updated = models.DateTimeField(default=now)
    created = models.DateTimeField(default=now)
    blurb = models.CharField(max_length=150, default=None)
    experience_with = models.ManyToManyField(TikedgeUser, default=None)

    def save(self, *args, **kwargs):
        if len(self.name_of_progress) > 150:
            self.blurb = self.name_of_progress[0:150]
        else:
            self.blurb = self.name_of_progress
        super(ProgressPicture, self).save(*args, **kwargs)

    def __str__(self):
        return '%s %s' % (self.name_of_progress, self.image_name)


class ProgressPictureSet(models.Model):
    list_of_progress_pictures = models.ManyToManyField(ProgressPicture)
    project = models.ForeignKey(UserProject, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    last_updated = models.DateTimeField(default=now)
    created = models.DateTimeField(default=now)
    is_empty = models.BooleanField(default=True)

    def __str__(self):
        return '%s' % self.project.name_of_project

    def picture_set_count(self):
        try:
            count = self.list_of_progress_pictures.filter(is_deleted=False).count()
        except ValueError:
            count = 0
        return count


class ShoutOutEmailAndNumber(models.Model):
    tikedge_user = models.ForeignKey(TikedgeUser, verbose_name="User that requested the shoutout")
    user_email_or_num = models.TextField(default=None)
    created = models.DateTimeField(default=now)
    is_email = models.BooleanField(default=False)
    is_number = models.BooleanField(default=True)
    progress_picture = models.ForeignKey(ProgressPicture, blank=True, null=True)
    email_or_text_sent = models.BooleanField(default=False)
    sent_date = models.DateTimeField(blank=True, null=True)
    user_responded = models.BooleanField(default=False)
    date_of_response = models.DateTimeField(blank=True, null=True)
    type_of_response = models.CharField(default="noResponse", max_length=250, verbose_name="user can respond by joining "
                                                                           "or not joining pondeye")


class PictureSet(models.Model):
    before_picture = models.ForeignKey(Picture, blank=True, null=True, related_name="before_picture")
    after_picture = models.ForeignKey(Picture, blank=True, null=True, related_name="after_picture")
    milestone = models.ForeignKey(Milestone, blank=True, null=True)
    tikedge_user = models.ForeignKey(TikedgeUser, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    last_updated = models.DateTimeField(default=now)

    def __str__(self):
        return '%s' % self.milestone.name_of_milestone


class Friends(models.Model):
    user = models.ForeignKey(TikedgeUser, blank=True, null=True)
    friends = models.ManyToManyField(TikedgeUser, related_name="user_friends")


class SeenMilestone(models.Model):
    users = models.ManyToManyField(TikedgeUser, verbose_name="Users That saw the milestones")
    tasks = models.ForeignKey(Milestone, blank=True, null=True)


class SeenProject(models.Model):
    users = models.ManyToManyField(TikedgeUser, verbose_name="Users That saw the projects")
    tasks = models.ForeignKey(UserProject, blank=True, null=True)

    def get_count(self):
        try:
            return self.users.count()
        except ValueError:
            return 0

    def __str__(self):
        return self.tasks.name_of_project


class SeenPictureSet(models.Model):
    users = models.ManyToManyField(TikedgeUser, verbose_name="Users That saw the pictureSet")
    tasks = models.ForeignKey(PictureSet, blank=True, null=True)


class SeenProgress(models.Model):
    users = models.ManyToManyField(TikedgeUser, verbose_name="Users That saw the pictureSet")
    tasks = models.ForeignKey(ProgressPicture, blank=True, null=True)

    def get_count(self):
        try:
            return self.users.count()
        except ValueError:
            return 0


class VoucheMilestone(models.Model):
    users = models.ManyToManyField(TikedgeUser, verbose_name="User That Vouche For the milestone")
    tasks = models.ForeignKey(Milestone, blank=True, null=True)
    latest_vouch = models.DateTimeField(default=now)

    def save(self, *args, **kwargs):
        self.latest_vouch = now()
        super(VoucheMilestone, self).save(*args, **kwargs)


class VoucheProject(models.Model):
    users = models.ManyToManyField(TikedgeUser, verbose_name="User That Vouche For the milestone")
    tasks = models.ForeignKey(UserProject, blank=True, null=True)
    latest_vouch = models.DateTimeField(default=now)

    def save(self, *args, **kwargs):
        self.latest_vouch = now()
        super(VoucheProject, self).save(*args, **kwargs)

    def __str__(self):
        return self.tasks.name_of_project

    def get_count(self):
        try:
            return self.users.count()
        except ValueError:
            return 0


class BuildCredMilestone(models.Model):
    users = models.ManyToManyField(TikedgeUser, verbose_name="User That Milestone Owner Built Cred For")
    tasks = models.ForeignKey(Milestone, blank=True, null=True)


class Follow(models.Model):
    users = models.ManyToManyField(TikedgeUser, verbose_name="users that follow/interested in a project")
    tasks = models.ForeignKey(UserProject, blank=True, null=True)
    latest_follow = models.DateTimeField(default=now)

    def save(self, *args, **kwargs):
        self.latest_follow = now()
        super(Follow, self).save(*args, **kwargs)

    def get_count(self):
        try:
            return self.users.count()
        except ValueError:
            return 0


class ProgressImpressedCount(models.Model):
    users = models.ManyToManyField(TikedgeUser, verbose_name="Users That saw the pictureSet")
    tasks = models.ForeignKey(ProgressPicture, blank=True, null=True)
    latest_impressed = models.DateTimeField(default=now)

    def get_count(self):
        try:
            return self.users.count()
        except ValueError:
            return 0

    def save(self, *args, **kwargs):
        self.latest_impressed = now()
        super(ProgressImpressedCount, self).save(*args, **kwargs)


class LetDownMilestone(models.Model):
    users = models.ManyToManyField(TikedgeUser, verbose_name="users that were let down by vouche for your Milestone")
    tasks = models.ForeignKey(Milestone, blank=True, null=True)
    latest_letDown = models.DateTimeField(default=now)

    def save(self, *args, **kwargs):
       self.latest_letDown = now()
       super(LetDownMilestone, self).save(*args, **kwargs)


class LetDownProject(models.Model):
    users = models.ManyToManyField(TikedgeUser, verbose_name="users that were let down by vouche for your Goal")
    tasks = models.ForeignKey(UserProject, blank=True, null=True)
    latest_letDown = models.DateTimeField(default=now)

    def save(self, *args, **kwargs):
       self.latest_letDown = now()
       super(LetDownProject, self).save(*args, **kwargs)

    def get_count(self):
       try:
           return self.users.count()
       except ValueError:
           return 0


class Notification(models.Model):
    friend_request = models.ForeignKey(FriendshipRequest, blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True)
    type_of_notification = models.CharField(max_length=100)
    created = models.DateTimeField(default=now)
    read = models.BooleanField(default=False)
    project_update = models.ForeignKey(UserProject, blank=True, null=True)
    name_of_notification = models.TextField(max_length=700, default="")
    id_of_object = models.IntegerField(default=0)
    date_read = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.type_of_notification


class JournalPost(models.Model):
    entry_blurb = models.CharField(default=None, max_length=240)
    day_entry = models.IntegerField(default=1)
    day_created = models.DateTimeField(default=now)
    event_type = models.CharField(default=PROJECT, max_length=20)
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
            the_slug = str_slug + str_slug_two + str(self.day_created)
            self.slug = slugify(the_slug)
        super(JournalPost, self).save(*args, **kwargs)


class JournalComment(models.Model):
    journal_post = models.ForeignKey(JournalPost, null=True)
    comment = models.CharField(max_length=2000, default=None)
    is_deleted = models.BooleanField(default=False)


class Pond(models.Model):
    name_of_pond = models.CharField(max_length=250)
    pond_creator = models.ForeignKey(TikedgeUser, null=True, blank=True, related_name='pond_creater')
    pond_members = models.ManyToManyField(TikedgeUser, related_name='pond_member')
    date_created = models.DateTimeField(default=now)
    date_deleted = models.DateTimeField(blank=True, null=True)
    tags = models.ManyToManyField(TagNames)
    slug = models.SlugField(default=None, max_length=100)
    purpose = models.CharField(max_length=110, default=None)
    blurb = models.CharField(max_length=51, default=None)
    is_deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if len(self.name_of_pond) > 50:
            self.blurb = self.name_of_pond[0:50]
        else:
            self.blurb = self.name_of_pond
        if not self.slug:
            str_slug = str(randint(0, 999999))
            str_slug_two = str(randint(9000, 99999999))
            the_slug = str_slug + str_slug_two + str(self.date_created)
            self.slug = slugify(the_slug)
        super(Pond, self).save(*args, **kwargs)

    def __str__(self):
        return self.name_of_pond


class PondProgressFeed(models.Model):
    name_of_feed = models.TextField(default=None)
    project = models.ForeignKey(UserProject, blank=False, null=True, related_name="project_pond_feed")
    pond = models.ForeignKey(Pond, blank=False, null=True)
    progress_picture = models.ForeignKey(ProgressPicture, blank=False, null=True, related_name="picture_pond_feed")

    def __str__(self):
         return '%s' % self.name_of_feed


class PondRequest(models.Model):
    user = models.ForeignKey(TikedgeUser, blank=True, null=True)
    pond = models.ForeignKey(Pond, blank=True, null=True)
    date_requested = models.DateTimeField(default=now)
    date_response = models.DateTimeField(blank=True, null=True)
    request_accepted = models.BooleanField(default=False)
    request_denied = models.BooleanField(default=False)
    request_responded_to = models.BooleanField(default=False)
    member_that_responded = models.ForeignKey(TikedgeUser, blank=True, null=True, related_name='the_member_that_responded')

    def __str__(self):
        return self.pond.name_of_pond


class PondMembership(models.Model):
    user = models.ForeignKey(TikedgeUser, blank=True, null=True)
    pond = models.ForeignKey(Pond, blank=True, null=True)
    date_joined = models.DateTimeField(default=now)
    date_removed = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.user.username


class PondSpecificProject(models.Model):
    project = models.ForeignKey(UserProject, blank=True, null=True)
    pond = models.ManyToManyField(Pond)

    def __str__(self):
        return self.project.name_of_project

    def get_count(self):
        try:
            return self.pond.count()
        except ValueError:
            return 0


class WorkEthicRank(models.Model):
    tikedge_user = models.ForeignKey(TikedgeUser, blank=True, null=True)
    consistency_rank = models.IntegerField(default=0)
    correct_vouching_rank = models.IntegerField(default=0)
    work_ethic_rank = models.IntegerField(default=0)

            







