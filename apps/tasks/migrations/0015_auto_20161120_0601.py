# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0014_auto_20161120_0557'),
    ]

    operations = [
        migrations.AddField(
            model_name='userproject',
            name='blurb',
            field=models.CharField(default=None, max_length=150),
        ),
        migrations.AddField(
            model_name='userproject',
            name='slug',
            field=models.SlugField(default=None, max_length=100),
        ),
    ]
