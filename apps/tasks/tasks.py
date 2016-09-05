from __future__ import absolute_import
from celery import shared_task
from .models import Tasks
from scheduler.celery import app
from .modules import time_to_utc
from django.utils import timezone

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
