# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0020_auto_20161123_0911'),
    ]

    operations = [
        migrations.RenameField(
            model_name='milestone',
            old_name='milestone_completed',
            new_name='is_failed',
        ),
        migrations.RenameField(
            model_name='userproject',
            old_name='date_past',
            new_name='is_failed',
        ),
        migrations.RemoveField(
            model_name='milestone',
            name='milestone_failed',
        ),
    ]
