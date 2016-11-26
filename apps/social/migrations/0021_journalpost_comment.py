# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0020_journalpost'),
    ]

    operations = [
        migrations.AddField(
            model_name='journalpost',
            name='comment',
            field=models.CharField(default=None, max_length=2000),
        ),
    ]
