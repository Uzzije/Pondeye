# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0003_taskpicture'),
    ]

    operations = [
        migrations.RenameField(
            model_name='taskpicture',
            old_name='profile_pics',
            new_name='task_pics',
        ),
    ]
