# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_auto_20160704_0028'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tasks',
            old_name='project_name',
            new_name='project',
        ),
    ]
