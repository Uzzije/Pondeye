from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from random import randint
from django.template.defaultfilters import slugify


class TikedgeUser(models.Model):
    user = models.OneToOneField(User)

    def __str__(self):
        return self.user.username


class TagNames(models.Model):
    name_of_tag = models.CharField(max_length=300)

    def __str__(self):
        return self.name_of_tag


class UserProject(models.Model):
    name_of_project = models.CharField(max_length=300)
    user = models.ForeignKey(TikedgeUser, blank=True, null=True)
    tags = models.ManyToManyField(TagNames)
    is_failed = models.BooleanField(default=False)
    is_live = models.BooleanField(default=False)
    length_of_project = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(default=now)
    made_live = models.DateTimeField(default=now)
    slug = models.SlugField(default=None, max_length=100)
    blurb = models.CharField(max_length=150, default=None)
    is_completed = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True, verbose_name="Can Be View By All People")
    is_deleted =  models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if len(self.name_of_project) > 150:
            self.blurb = self.name_of_project[0:150]
        else:
            self.blurb = self.name_of_project
        if not self.slug:
            str_slug = str(randint(0, 999999))
            str_slug_two = str(randint(9000, 99999999))
            the_slug = str_slug + str_slug_two + str(self.created)
            self.slug = slugify(the_slug)
        super(UserProject, self).save(*args, **kwargs)

    def __str__(self):
        return self.name_of_project


class Milestone(models.Model):
    name_of_milestone = models.CharField(max_length=600)
    project = models.ForeignKey(UserProject, blank=True, null=True)
    user = models.ForeignKey(TikedgeUser, blank=True, null=True)
    reminder = models.DateTimeField(blank=True, null=True)
    done_by = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_failed = models.BooleanField(default=False)
    current_working_on_milestone = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=now)
    slug = models.SlugField(default=None, max_length=100)
    blurb = models.CharField(max_length=150, default=None)
    is_completed = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    last_update = models.DateTimeField(default=now)

    def __str__(self):
        return self.name_of_milestone

    def save(self, *args, **kwargs):
        if len(self.name_of_milestone) > 150:
            self.blurb = self.name_of_milestone[0:150]
        else:
            self.blurb = self.name_of_milestone
        if not self.slug:
            str_slug = str(randint(0, 999999))
            str_slug_two = str(randint(9000, 99999999))
            self.slug = str_slug + str_slug_two
        super(Milestone, self).save(*args, **kwargs)


class LaunchEmail(models.Model):
    email = models.CharField(max_length=150)
