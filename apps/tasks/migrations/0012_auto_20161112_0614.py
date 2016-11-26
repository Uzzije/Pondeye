# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0011_auto_20161112_0524'),
    ]

    operations = [
        migrations.AddField(
            model_name='userproject',
            name='date_past',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userproject',
            name='is_live',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userproject',
            name='length_of_project',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
