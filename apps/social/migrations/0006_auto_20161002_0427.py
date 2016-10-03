# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import image_cropping.fields


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0005_auto_20161002_0427'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profilepictures',
            name=b'cropping',
            field=image_cropping.fields.ImageRatioField('profile_pics', '5x5', hide_image_field=False, size_warning=False, allow_fullsize=False, free_crop=False, adapt_rotation=False, help_text=None, verbose_name='cropping'),
        ),
        migrations.AlterField(
            model_name='taskpicture',
            name=b'cropping',
            field=image_cropping.fields.ImageRatioField('task_pics', '5x5', hide_image_field=False, size_warning=False, allow_fullsize=False, free_crop=False, adapt_rotation=False, help_text=None, verbose_name='cropping'),
        ),
    ]
