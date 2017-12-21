# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_userproject_made_progress'),
        ('social', '0005_auto_20171219_2026'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChallengeNotification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.TextField(default='', max_length=700)),
                ('read', models.BooleanField(default=False)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_read', models.DateTimeField(null=True, blank=True)),
                ('challenge', models.ForeignKey(blank=True, to='social.Challenge', null=True)),
                ('from_user', models.ForeignKey(related_name='challenged_initiated_by_user', blank=True, to='tasks.TikedgeUser', null=True)),
                ('to_user', models.ForeignKey(related_name='challenged_owner_notification', blank=True, to='tasks.TikedgeUser', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='FriendshipNotification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.TextField(default='', max_length=700)),
                ('read', models.BooleanField(default=False)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_read', models.DateTimeField(null=True, blank=True)),
                ('from_user', models.ForeignKey(related_name='friendship_initiated_by_user', blank=True, to='tasks.TikedgeUser', null=True)),
                ('to_user', models.ForeignKey(related_name='friendship_owner_notification', blank=True, to='tasks.TikedgeUser', null=True)),
            ],
        ),
    ]
