# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0006_auto_20160708_0412'),
    ]

    operations = [
        migrations.CreateModel(
            name='PendingTasks',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('remind_user', models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterField(
            model_name='tasks',
            name='start',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='pendingtasks',
            name='tasks',
            field=models.ManyToManyField(to='tasks.Tasks'),
        ),
        migrations.AddField(
            model_name='pendingtasks',
            name='tikedge_user',
            field=models.ForeignKey(blank=True, to='tasks.TikedgeUser', null=True),
        ),
    ]
