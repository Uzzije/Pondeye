# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0012_auto_20161016_2141'),
    ]

    operations = [
        migrations.AddField(
            model_name='graded',
            name='max_consistency_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='graded',
            name='max_credibility_count',
            field=models.IntegerField(default=0),
        ),
    ]
