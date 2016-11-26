# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0010_milestone'),
    ]

    operations = [
        migrations.CreateModel(
            name='TagNames',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_of_tag', models.CharField(max_length=300)),
            ],
        ),
        migrations.AddField(
            model_name='userproject',
            name='tags',
            field=models.ManyToManyField(to='tasks.TagNames'),
        ),
    ]
