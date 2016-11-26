# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0026_auto_20161126_2224'),
        ('tasks', '0021_auto_20161123_1848'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pendingtasks',
            name='tasks',
        ),
        migrations.RemoveField(
            model_name='pendingtasks',
            name='tikedge_user',
        ),
        migrations.RemoveField(
            model_name='tasks',
            name='project',
        ),
        migrations.RemoveField(
            model_name='tasks',
            name='user',
        ),
        migrations.DeleteModel(
            name='PendingTasks',
        ),
        migrations.DeleteModel(
            name='Tasks',
        ),
    ]
