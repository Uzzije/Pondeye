# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0009_pendingtasks_is_removed'),
    ]

    operations = [
        migrations.CreateModel(
            name='Milestone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_of_milestone', models.CharField(max_length=300)),
                ('reminder', models.DateTimeField(null=True, blank=True)),
                ('done_by', models.DateTimeField(null=True, blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('milestone_completed', models.BooleanField(default=False)),
                ('milestone_failed', models.BooleanField(default=False)),
                ('current_working_on_milestone', models.BooleanField(default=False)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('project', models.ForeignKey(blank=True, to='tasks.UserProject', null=True)),
                ('user', models.ForeignKey(blank=True, to='tasks.TikedgeUser', null=True)),
            ],
        ),
    ]
