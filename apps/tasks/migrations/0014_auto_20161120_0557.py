# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0013_auto_20161112_0621'),
    ]

    operations = [
        migrations.AddField(
            model_name='milestone',
            name='blurb',
            field=models.CharField(default=None, max_length=150),
        ),
        migrations.AddField(
            model_name='milestone',
            name='slug',
            field=models.SlugField(default=None, max_length=100),
        ),
    ]
