# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0014_auto_20161016_2251'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='name_of_notification',
            field=models.CharField(default='', max_length=300),
        ),
    ]
