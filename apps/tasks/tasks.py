from __future__ import absolute_import
from scheduler.celery import app
from django.core.exceptions import ObjectDoesNotExist
from celery.task import periodic_task
from datetime import timedelta, datetime
import logging
from ..social.modules import make_timeline_video
from ..social.models import ProgressVideoSet
from .models import UserProject

logger = logging.getLogger(__name__)
'''
@app.task
def set_reminder(pk):
    try:
        tasks = Tasks.objects.get(pk=pk)
        tasks.is_active = False
        tasks.save()
    except ObjectDoesNotExist:
        pass


@app.task
def set_task_active(pk):
    try:
        tasks = Tasks.objects.get(pk=pk)
        tasks.current_working_on_task = True
        tasks.save()
    except ObjectDoesNotExist:
        pass


@app.task
def set_reminder_for_non_committed_tasks(pk):
    pending_task = PendingTasks.objects.get(pk=pk)
    if pending_task.tasks.all().count() > 0:
        pending_task.remind_user = True
    else:
        pending_task.remind_user = False
    pending_task.save()
'''


@app.task
def begin_timeline_video(proj_id):
    proj_stone = UserProject.objects.get(id=proj_id)
    progress_set = ProgressVideoSet.objects.get(challenge__project=proj_stone)
    logger.info("Creating New Highlight Video for this goal: %s" % progress_set.challenge.project.name_of_project)
    """
    proj_stone.is_completed = True
    proj_stone.is_live = False
    proj_stone.save()
    """
    proj_stone.cc_job_began = True
    proj_stone.save()
    try:
        make_timeline_video(progress_set)
    except OSError:
        proj_stone.cc_job_began = False
        proj_stone.save()




# coding=utf-8

# A periodic task that will run every minute (the symbol "*" means every)
# A periodic task that will run every minute (the symbol "*" means every)