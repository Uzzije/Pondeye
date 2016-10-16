# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0010_graded_tasks'),
    ]

    operations = [
        migrations.RenameField(
            model_name='graded',
            old_name='tasks',
            new_name='user',
        ),
    ]
