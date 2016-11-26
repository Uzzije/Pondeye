# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0022_auto_20161121_1645'),
    ]

    operations = [
        migrations.AddField(
            model_name='journalpost',
            name='entry_blurb',
            field=models.CharField(default=None, max_length=240),
        ),
        migrations.AddField(
            model_name='journalpost',
            name='is_milestone_entry',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='journalpost',
            name='is_picture_set',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='journalpost',
            name='is_project_entry',
            field=models.BooleanField(default=False),
        ),
    ]
