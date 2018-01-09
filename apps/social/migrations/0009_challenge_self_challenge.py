# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0008_auto_20180109_1956'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='self_challenge',
            field=models.BooleanField(default=False),
        ),
    ]
