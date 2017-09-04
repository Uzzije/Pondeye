from __future__ import absolute_import
from .models import Tasks, PendingTasks, TikedgeUser
from scheduler.celery import app
from django.core.exceptions import ObjectDoesNotExist



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
