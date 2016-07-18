# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('friendship', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tasks', '0006_auto_20160708_0412'),
        ('social', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BuildCred',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tasks', models.ForeignKey(blank=True, to='tasks.Tasks', null=True)),
                ('users', models.ManyToManyField(to='tasks.TikedgeUser', verbose_name='User That Tasks Owner Built Cred For')),
            ],
        ),
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tasks', models.ForeignKey(blank=True, to='tasks.UserProject', null=True)),
                ('users', models.ManyToManyField(to='tasks.TikedgeUser', verbose_name='users that follow a project')),
            ],
        ),
        migrations.CreateModel(
            name='Friends',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('friends', models.ManyToManyField(related_name='user_friends', to='tasks.TikedgeUser')),
                ('user', models.ForeignKey(blank=True, to='tasks.TikedgeUser', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LetDown',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tasks', models.ForeignKey(blank=True, to='tasks.Tasks', null=True)),
                ('users', models.ManyToManyField(to='tasks.TikedgeUser', verbose_name='users that were let down by vouche for your task')),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type_of_notification', models.CharField(max_length=100)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('read', models.BooleanField(default=False)),
                ('friend_request', models.ForeignKey(blank=True, to='friendship.FriendshipRequest', null=True)),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Seen',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tasks', models.ForeignKey(blank=True, to='tasks.Tasks', null=True)),
                ('users', models.ManyToManyField(to='tasks.TikedgeUser', verbose_name='Users That saw the tasks')),
            ],
        ),
        migrations.CreateModel(
            name='Vouche',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tasks', models.ForeignKey(blank=True, to='tasks.Tasks', null=True)),
                ('users', models.ManyToManyField(to='tasks.TikedgeUser', verbose_name='User That Vouche For the Task')),
            ],
        ),
    ]
