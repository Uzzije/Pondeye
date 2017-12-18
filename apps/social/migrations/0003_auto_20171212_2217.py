# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
        ('social', '0002_progressvideo_project'),
    ]

    operations = [
        migrations.CreateModel(
            name='Challenge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('challenge_responded', models.BooleanField(default=False)),
                ('challenge_accepted', models.BooleanField(default=False)),
                ('challenge_rejected', models.BooleanField(default=False)),
                ('challenged', models.ForeignKey(related_name='the_challenged', blank=True, to='tasks.TikedgeUser', null=True)),
                ('challenger', models.ForeignKey(blank=True, to='tasks.TikedgeUser', null=True)),
                ('project', models.ForeignKey(blank=True, to='tasks.UserProject', null=True)),
            ],
        ),
        migrations.RenameModel(
            old_name='ProjectVideo',
            new_name='ChallengeVideo',
        ),
        migrations.RemoveField(
            model_name='challengevideo',
            name='project',
        ),
        migrations.RemoveField(
            model_name='shoutoutemailandnumber',
            name='is_picture_shout_outs',
        ),
        migrations.AddField(
            model_name='challengevideo',
            name='challenge',
            field=models.ForeignKey(blank=True, to='social.Challenge', null=True),
        ),
    ]
