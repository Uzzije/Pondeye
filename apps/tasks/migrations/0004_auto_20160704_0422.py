# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_auto_20160704_0302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tasks',
            name='end',
            field=models.DateTimeField(default=django.utils.timezone.now, blank=True),
        ),
        migrations.AlterField(
            model_name='tasks',
            name='start',
            field=models.DateTimeField(default=django.utils.timezone.now, blank=True),
        ),
    ]
