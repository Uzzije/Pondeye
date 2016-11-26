# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0013_auto_20161112_0621'),
        ('social', '0018_auto_20161112_2209'),
    ]

    operations = [
        migrations.CreateModel(
            name='BuildCredMilestone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tasks', models.ForeignKey(blank=True, to='tasks.Milestone', null=True)),
                ('users', models.ManyToManyField(to='tasks.TikedgeUser', verbose_name='User That Milestone Owner Built Cred For')),
            ],
        ),
        migrations.CreateModel(
            name='LetDownMilestone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tasks', models.ForeignKey(blank=True, to='tasks.Milestone', null=True)),
                ('users', models.ManyToManyField(to='tasks.TikedgeUser', verbose_name='users that were let down by vouche for your Milestone')),
            ],
        ),
        migrations.CreateModel(
            name='SeenMilestone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tasks', models.ForeignKey(blank=True, to='tasks.Milestone', null=True)),
                ('users', models.ManyToManyField(to='tasks.TikedgeUser', verbose_name='Users That saw the milestones')),
            ],
        ),
        migrations.CreateModel(
            name='SeenPictureSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tasks', models.ForeignKey(blank=True, to='social.PictureSet', null=True)),
                ('users', models.ManyToManyField(to='tasks.TikedgeUser', verbose_name='Users That saw the pictureSet')),
            ],
        ),
        migrations.CreateModel(
            name='SeenProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tasks', models.ForeignKey(blank=True, to='tasks.UserProject', null=True)),
                ('users', models.ManyToManyField(to='tasks.TikedgeUser', verbose_name='Users That saw the projects')),
            ],
        ),
        migrations.CreateModel(
            name='VoucheMilestone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tasks', models.ForeignKey(blank=True, to='tasks.Milestone', null=True)),
                ('users', models.ManyToManyField(to='tasks.TikedgeUser', verbose_name='User That Vouche For the milestone')),
            ],
        ),
    ]
