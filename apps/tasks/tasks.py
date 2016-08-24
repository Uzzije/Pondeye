from __future__ import absolute_import
from celery import Celery
from tasks.models import Tasks

app = Celery('tasks', broker='amqp://guest@localhost//')

@app.task
def print_reminder(pk):
    task = Tasks.objects.get(pk=pk)
    print 'mandem_sucks', task.name_of_tasks