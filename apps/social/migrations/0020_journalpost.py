# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0017_auto_20161120_0720'),
        ('social', '0019_buildcredmilestone_letdownmilestone_seenmilestone_seenpictureset_seenproject_vouchemilestone'),
    ]

    operations = [
        migrations.CreateModel(
            name='JournalPost',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('day_entry', models.IntegerField(default=1)),
                ('day_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('event_type', models.CharField(default=b'np', max_length=20)),
                ('is_deleted', models.BooleanField(default=False)),
                ('milestone_entry', models.ForeignKey(to='tasks.Milestone', null=True)),
                ('new_project_entry', models.ForeignKey(to='tasks.UserProject', null=True)),
                ('picture_set_entry', models.ForeignKey(to='social.PictureSet', null=True)),
                ('user', models.ForeignKey(to='tasks.TikedgeUser', null=True)),
            ],
        ),
    ]
