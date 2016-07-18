# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tasks',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_of_tasks', models.CharField(max_length=300)),
                ('part_of_project', models.BooleanField(default=False)),
                ('start', models.DateTimeField(blank=True)),
                ('end', models.DateTimeField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_of_project', models.CharField(max_length=300)),
                ('user', models.ForeignKey(blank=True, to='tasks.TikedgeUser', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='tasks',
            name='project_name',
            field=models.ForeignKey(blank=True, to='tasks.UserProject', null=True),
        ),
        migrations.AddField(
            model_name='tasks',
            name='user',
            field=models.ForeignKey(blank=True, to='tasks.TikedgeUser', null=True),
        ),
    ]
