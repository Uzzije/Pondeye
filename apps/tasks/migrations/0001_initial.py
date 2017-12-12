# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LaunchEmail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='Milestone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_of_milestone', models.CharField(max_length=600)),
                ('reminder', models.DateTimeField(null=True, blank=True)),
                ('done_by', models.DateTimeField(null=True, blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_failed', models.BooleanField(default=False)),
                ('current_working_on_milestone', models.BooleanField(default=False)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('slug', models.SlugField(default=None, max_length=100)),
                ('blurb', models.CharField(default=None, max_length=150)),
                ('is_completed', models.BooleanField(default=False)),
                ('is_deleted', models.BooleanField(default=False)),
                ('last_update', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='PasswordReset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('token', models.CharField(default='75876uhudi', max_length=12)),
                ('was_used', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TagNames',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_of_tag', models.CharField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='TikedgeUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(default=None, max_length=100)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_of_project', models.TextField(max_length=300)),
                ('is_failed', models.BooleanField(default=False)),
                ('is_live', models.BooleanField(default=False)),
                ('length_of_project', models.DateTimeField(null=True, blank=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('made_live', models.DateTimeField(default=django.utils.timezone.now)),
                ('slug', models.SlugField(default=None, max_length=100)),
                ('blurb', models.CharField(default=None, max_length=150)),
                ('is_completed', models.BooleanField(default=False)),
                ('is_public', models.BooleanField(default=True, verbose_name='Can Be View By All People')),
                ('is_deleted', models.BooleanField(default=False)),
                ('last_update', models.DateTimeField(default=django.utils.timezone.now)),
                ('tags', models.ManyToManyField(to='tasks.TagNames')),
                ('user', models.ForeignKey(blank=True, to='tasks.TikedgeUser', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='milestone',
            name='project',
            field=models.ForeignKey(blank=True, to='tasks.UserProject', null=True),
        ),
        migrations.AddField(
            model_name='milestone',
            name='user',
            field=models.ForeignKey(blank=True, to='tasks.TikedgeUser', null=True),
        ),
    ]
