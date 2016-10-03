# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0007_auto_20161002_2303'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profilepictures',
            old_name='tikede_user',
            new_name='tikedge_user',
        ),
        migrations.RenameField(
            model_name='taskpicture',
            old_name='tikede_user',
            new_name='tikedge_user',
        ),
    ]
