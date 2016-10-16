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
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
    task_completed = models.BooleanField(default=False)
    task_failed = models.BooleanField(default=False)
    current_working_on_task = models.BooleanField(default=False)
    publish_date = models.DateTimeField(default=now)

    def __str__(self):
        return self.name_of_tasks


class PendingTasks(models.Model):
    tasks = models.ManyToManyField(Tasks)
    tikedge_user = models.ForeignKey(TikedgeUser, blank=True, null=True)
    remind_user = models.BooleanField(default=False)
    is_removed = models.BooleanField(default=False)


