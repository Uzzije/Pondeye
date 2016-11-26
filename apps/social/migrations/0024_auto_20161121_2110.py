# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0023_auto_20161121_2006'),
    ]

    operations = [
        migrations.AddField(
            model_name='journalcomment',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='journalpost',
            name='slug',
            field=models.SlugField(default=None, max_length=100),
        ),
    ]
