# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0005_tasks_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='tasks',
            name='current_working_on_task',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='tasks',
            name='task_completed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='tasks',
            name='task_failed',
            field=models.BooleanField(default=False),
        ),
    ]
