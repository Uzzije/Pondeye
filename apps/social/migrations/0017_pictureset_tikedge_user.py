# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0013_auto_20161112_0621'),
        ('social', '0016_picture_pictureset'),
    ]

    operations = [
        migrations.AddField(
            model_name='pictureset',
            name='tikedge_user',
            field=models.ForeignKey(blank=True, to='tasks.TikedgeUser', null=True),
        ),
    ]
