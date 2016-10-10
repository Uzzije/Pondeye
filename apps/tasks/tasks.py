from __future__ import absolute_import
from .models import Tasks
from scheduler.celery import app
from .global_variables_tasks import NON_DATED_TASKS_FLAGS


@app.task
def set_reminder(pk):
    tasks = Tasks.objects.get(pk=pk)
    tasks.is_active = False
    tasks.save()


@app.task
def set_task_active(pk):
    tasks = Tasks.objects.get(pk=pk)
    tasks.current_working_on_task = True
    tasks.save()

@app.task
def set_reminder_for_non_committed_tasks(pk):
    pass