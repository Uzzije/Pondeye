# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0016_auto_20161120_0628'),
    ]

    operations = [
        migrations.AlterField(
            model_name='milestone',
            name='name_of_milestone',
            field=models.CharField(max_length=600),
        ),
    ]
