# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_userproject_made_progress'),
        ('social', '0006_challengenotification_friendshipnotification'),
    ]

    operations = [
        migrations.CreateModel(
            name='HighlightImpressedCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('progress_set', models.ForeignKey(blank=True, to='social.ProgressVideoSet', null=True)),
                ('users', models.ForeignKey(verbose_name='Users impressed by recent highlight', to='tasks.TikedgeUser')),
            ],
        ),
        migrations.CreateModel(
            name='RecentUploadImpressedCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('progress', models.ForeignKey(blank=True, to='social.ProgressVideo', null=True)),
                ('users', models.ForeignKey(verbose_name='Users impressed by recent progress', to='tasks.TikedgeUser')),
            ],
        ),
    ]
