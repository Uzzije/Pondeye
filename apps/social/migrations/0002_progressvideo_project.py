# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
        ('social', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='progressvideo',
            name='project',
            field=models.ForeignKey(blank=True, to='tasks.UserProject', null=True),
        ),
    ]
