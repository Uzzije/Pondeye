from __future__ import absolute_import
from scheduler.celery import app
from django.core.exceptions import ObjectDoesNotExist
from celery.task import periodic_task
from datetime import timedelta, datetime
import logging
logger = logging.getLogger(__name__)
from social.modules import make_timeline_video

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
def begin_timeline_video(progress_set):
    make_timeline_video(progress_set)
    logger.info("Create New Highlight Video for this goal: %s" % progress_set.project.name_of_project)


# coding=utf-8

# A periodic task that will run every minute (the symbol "*" means every)
# A periodic task that will run every minute (the symbol "*" means every)


@periodic_task(run_every=timedelta(minutes=1))
def sample_periodic_task():
    logger.info("Start task")
    now = datetime.now()
    result = now.day + now.minute
    logger.info("Task finished: result = %i" % result)