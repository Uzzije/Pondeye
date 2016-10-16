# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0007_auto_20161015_0424'),
    ]

    operations = [
        migrations.AddField(
            model_name='tasks',
            name='publish_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='tasks',
            name='end',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
