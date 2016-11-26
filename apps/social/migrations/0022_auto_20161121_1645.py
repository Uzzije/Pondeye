# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0021_journalpost_comment'),
    ]

    operations = [
        migrations.CreateModel(
            name='JournalComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.CharField(default=None, max_length=2000)),
            ],
        ),
        migrations.RemoveField(
            model_name='journalpost',
            name='comment',
        ),
        migrations.AddField(
            model_name='journalcomment',
            name='journal_post',
            field=models.ForeignKey(to='social.JournalPost', null=True),
        ),
    ]
