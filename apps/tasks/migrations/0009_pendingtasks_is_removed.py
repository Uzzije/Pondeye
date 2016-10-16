# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0008_auto_20161015_0810'),
    ]

    operations = [
        migrations.AddField(
            model_name='pendingtasks',
            name='is_removed',
            field=models.BooleanField(default=False),
        ),
    ]
