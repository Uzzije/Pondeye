# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0024_auto_20161121_2110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='follow',
            name='users',
            field=models.ManyToManyField(to='tasks.TikedgeUser', verbose_name='users that follow/interested in a project'),
        ),
    ]
