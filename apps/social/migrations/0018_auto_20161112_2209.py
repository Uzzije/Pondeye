# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import image_cropping.fields


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0017_pictureset_tikedge_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='picture',
            name=b'cropping',
            field=image_cropping.fields.ImageRatioField('milestone_pics', '5x5', hide_image_field=False, size_warning=False, allow_fullsize=False, free_crop=False, adapt_rotation=False, help_text=None, verbose_name='cropping'),
        ),
    ]
