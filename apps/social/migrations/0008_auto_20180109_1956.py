# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0007_highlightimpressedcount_recentuploadimpressedcount'),
    ]

    operations = [
        migrations.AddField(
            model_name='commentchallengeacceptance',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='commentrecentuploads',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='commentrecentuploads',
            name='recent_upload',
            field=models.ForeignKey(blank=True, to='social.ProgressVideo', null=True),
        ),
        migrations.AddField(
            model_name='commentrequestfeed',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='commentvideocelebrations',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
