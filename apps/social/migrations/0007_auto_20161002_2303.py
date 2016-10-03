# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0006_auto_20160708_0412'),
        ('social', '0006_auto_20161002_0427'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='picture_post',
            field=models.ForeignKey(blank=True, to='social.TaskPicture', null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='project_update',
            field=models.ForeignKey(blank=True, to='tasks.UserProject', null=True),
        ),
        migrations.AddField(
            model_name='profilepictures',
            name='date_uploaded',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='taskpicture',
            name='date_uploaded',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
