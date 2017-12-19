# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0004_auto_20171218_0551'),
    ]

    operations = [
        migrations.AlterField(
            model_name='challenge',
            name='date_responded',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
