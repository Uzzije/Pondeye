from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class TikedgeUser(models.Model):
    user = models.OneToOneField(User)

    def __str__(self):
        return self.user.username


class UserProject(models.Model):
    name_of_project = models.CharField(max_length=300)
    user = models.ForeignKey(TikedgeUser, blank=True, null=True)


class Tasks(models.Model):
    name_of_tasks = models.CharField(max_length=300)
    part_of_project = models.BooleanField(default=False)
    project = models.ForeignKey(UserProject, blank=True, null=True)
    user = models.ForeignKey(TikedgeUser, blank=True, null=True)
    start = models.DateTimeField(blank=True, default=now)
    end = models.DateTimeField(blank=True, default=now)
    is_active = models.BooleanField(default=False)
    task_completed = models.BooleanField(default=False)
    task_failed = models.BooleanField(default=False)
    current_working_on_task = models.BooleanField(default=False)

    def __str__(self):
        return self.name_of_tasks
