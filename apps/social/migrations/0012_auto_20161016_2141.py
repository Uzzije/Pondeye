# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0011_auto_20161016_0435'),
    ]

    operations = [
        migrations.AddField(
            model_name='graded',
            name='prior_crediblity_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='notification',
            name='name_of_notification',
            field=models.CharField(default='No Notifications', max_length=300),
        ),
    ]
