# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import image_cropping.fields


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0013_auto_20161112_0621'),
        ('social', '0015_auto_20161112_0319'),
    ]

    operations = [
        migrations.CreateModel(
            name='Picture',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image_name', models.CharField(max_length=300)),
                ('milestone_pics', models.ImageField(upload_to='image/tasks/%Y/%m/%d', verbose_name='profile image')),
                (b'cropping', image_cropping.fields.ImageRatioField('task_pics', '5x5', hide_image_field=False, size_warning=False, allow_fullsize=False, free_crop=False, adapt_rotation=False, help_text=None, verbose_name='cropping')),
                ('date_uploaded', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_before', models.BooleanField(default=True)),
                ('tikedge_user', models.ForeignKey(blank=True, to='tasks.TikedgeUser', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PictureSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('after_picture', models.ForeignKey(related_name='after_picture', blank=True, to='social.Picture', null=True)),
                ('before_picture', models.ForeignKey(related_name='before_picture', blank=True, to='social.Picture', null=True)),
                ('milestone', models.ForeignKey(blank=True, to='tasks.Milestone', null=True)),
            ],
        ),
    ]
