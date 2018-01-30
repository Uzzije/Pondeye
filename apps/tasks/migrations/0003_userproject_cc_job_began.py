# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_userproject_made_progress'),
    ]

    operations = [
        migrations.AddField(
            model_name='userproject',
            name='cc_job_began',
            field=models.BooleanField(default=False, verbose_name='Job to create highlight has began'),
        ),
    ]
