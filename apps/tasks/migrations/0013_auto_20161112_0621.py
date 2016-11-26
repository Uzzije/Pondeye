# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0012_auto_20161112_0614'),
    ]

    operations = [
        migrations.AddField(
            model_name='userproject',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='userproject',
            name='made_live',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
