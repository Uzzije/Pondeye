# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0009_pendingtasks_is_removed'),
        ('social', '0009_auto_20161016_0428'),
    ]

    operations = [
        migrations.AddField(
            model_name='graded',
            name='tasks',
            field=models.ForeignKey(blank=True, to='tasks.TikedgeUser', null=True),
        ),
    ]
