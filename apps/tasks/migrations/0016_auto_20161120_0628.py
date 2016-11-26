# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0015_auto_20161120_0601'),
    ]

    operations = [
        migrations.AddField(
            model_name='milestone',
            name='is_completed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userproject',
            name='is_completed',
            field=models.BooleanField(default=False),
        ),
    ]
