# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0017_auto_20161120_0720'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userproject',
            name='made_live',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
