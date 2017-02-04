# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0002_remove_profilepictures_is_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='profilepictures',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
