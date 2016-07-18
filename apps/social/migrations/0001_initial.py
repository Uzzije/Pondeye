# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import image_cropping.fields


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0006_auto_20160708_0412'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfilePictures',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image_name', models.CharField(max_length=100)),
                ('profile_pics', models.ImageField(upload_to='image/%Y/%m/%d', verbose_name='profile image')),
                (b'cropping', image_cropping.fields.ImageRatioField('profile_pics', '60x60', hide_image_field=False, size_warning=False, allow_fullsize=False, free_crop=False, adapt_rotation=False, help_text=None, verbose_name='cropping')),
                ('tikede_user', models.ForeignKey(blank=True, to='tasks.TikedgeUser', null=True)),
            ],
        ),
    ]
