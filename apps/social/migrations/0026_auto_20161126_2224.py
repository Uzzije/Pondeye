# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0025_auto_20161122_2349'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='buildcred',
            name='tasks',
        ),
        migrations.RemoveField(
            model_name='buildcred',
            name='users',
        ),
        migrations.RemoveField(
            model_name='letdown',
            name='tasks',
        ),
        migrations.RemoveField(
            model_name='letdown',
            name='users',
        ),
        migrations.RemoveField(
            model_name='seen',
            name='tasks',
        ),
        migrations.RemoveField(
            model_name='seen',
            name='users',
        ),
        migrations.RemoveField(
            model_name='taskpicture',
            name='task',
        ),
        migrations.RemoveField(
            model_name='taskpicture',
            name='tikedge_user',
        ),
        migrations.RemoveField(
            model_name='vouche',
            name='tasks',
        ),
        migrations.RemoveField(
            model_name='vouche',
            name='users',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='picture_post',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='tasks',
        ),
        migrations.DeleteModel(
            name='BuildCred',
        ),
        migrations.DeleteModel(
            name='LetDown',
        ),
        migrations.DeleteModel(
            name='Seen',
        ),
        migrations.DeleteModel(
            name='TaskPicture',
        ),
        migrations.DeleteModel(
            name='Vouche',
        ),
    ]
