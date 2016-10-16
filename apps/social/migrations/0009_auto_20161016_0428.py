# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0009_pendingtasks_is_removed'),
        ('social', '0008_auto_20161002_2340'),
    ]

    operations = [
        migrations.CreateModel(
            name='Graded',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('credibility_count', models.IntegerField(default=0)),
                ('consistency_count', models.IntegerField(default=0)),
                ('correct_vouch', models.IntegerField(default=0)),
                ('seen_vouch_fail', models.IntegerField(default=0)),
                ('seen_without_vouch', models.IntegerField(default=0)),
                ('failed_tasks', models.IntegerField(default=0)),
                ('completed_tasks', models.IntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='notification',
            name='tasks',
            field=models.ForeignKey(blank=True, to='tasks.Tasks', null=True),
        ),
    ]
