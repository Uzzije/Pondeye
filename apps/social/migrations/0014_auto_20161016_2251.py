# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0013_auto_20161016_2214'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='graded',
            name='seen_vouch_fail',
        ),
        migrations.RemoveField(
            model_name='graded',
            name='seen_without_vouch',
        ),
        migrations.AddField(
            model_name='graded',
            name='prior_consitency_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='graded',
            name='seen_without_vouch_fail',
            field=models.IntegerField(default=0, verbose_name="user saw tasks thats that didn't get done, and didn't vouche for it"),
        ),
        migrations.AddField(
            model_name='graded',
            name='seen_without_vouch_success',
            field=models.IntegerField(default=0, verbose_name="user saw a tasks that got completed, but didn't vouche for it"),
        ),
        migrations.AddField(
            model_name='graded',
            name='vouch_fail',
            field=models.IntegerField(default=0, verbose_name="user vouch for tasks that didn't get done"),
        ),
        migrations.AlterField(
            model_name='graded',
            name='correct_vouch',
            field=models.IntegerField(default=0, verbose_name='user vouch for tasks that got done'),
        ),
    ]
