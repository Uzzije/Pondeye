# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_userproject_made_progress'),
        ('social', '0003_auto_20171212_2217'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChallengeRating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.IntegerField(default=0)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='CommentChallengeAcceptance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.TextField(default='', max_length=500)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='CommentRecentUploads',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.TextField(default='', max_length=500)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='CommentRequestFeed',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.TextField(default='', max_length=500)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='CommentVideoCelebrations',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.TextField(default='', max_length=500)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='FollowChallenge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_followed', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='SeenChallenge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='SeenRecentUpload',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tikedge_user', models.ForeignKey(blank=True, to='tasks.TikedgeUser', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SeenVideoSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tikedge_user', models.ForeignKey(blank=True, to='tasks.TikedgeUser', null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='progressvideo',
            name='project',
        ),
        migrations.RemoveField(
            model_name='progressvideoset',
            name='project',
        ),
        migrations.AddField(
            model_name='challenge',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='challenge',
            name='date_responded',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='challenge',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='challenge',
            name='is_public',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='progressvideo',
            name='challenge',
            field=models.ForeignKey(blank=True, to='social.Challenge', null=True),
        ),
        migrations.AddField(
            model_name='progressvideoset',
            name='challenge',
            field=models.ForeignKey(blank=True, to='social.Challenge', null=True),
        ),
        migrations.AddField(
            model_name='seenvideoset',
            name='video_set',
            field=models.ForeignKey(blank=True, to='social.ProgressVideoSet', null=True),
        ),
        migrations.AddField(
            model_name='seenrecentupload',
            name='video',
            field=models.ForeignKey(blank=True, to='social.ProgressVideo', null=True),
        ),
        migrations.AddField(
            model_name='seenchallenge',
            name='challenge',
            field=models.ForeignKey(blank=True, to='social.Challenge', null=True),
        ),
        migrations.AddField(
            model_name='seenchallenge',
            name='tikedge_user',
            field=models.ForeignKey(blank=True, to='tasks.TikedgeUser', null=True),
        ),
        migrations.AddField(
            model_name='followchallenge',
            name='challenge',
            field=models.ForeignKey(blank=True, to='social.Challenge', null=True),
        ),
        migrations.AddField(
            model_name='followchallenge',
            name='users',
            field=models.ForeignKey(verbose_name='users that follow/interested in a project', to='tasks.TikedgeUser'),
        ),
        migrations.AddField(
            model_name='commentvideocelebrations',
            name='challenge',
            field=models.ForeignKey(blank=True, to='social.Challenge', null=True),
        ),
        migrations.AddField(
            model_name='commentvideocelebrations',
            name='tikedge_user',
            field=models.ForeignKey(blank=True, to='tasks.TikedgeUser', null=True),
        ),
        migrations.AddField(
            model_name='commentrequestfeed',
            name='challenge',
            field=models.ForeignKey(blank=True, to='social.Challenge', null=True),
        ),
        migrations.AddField(
            model_name='commentrequestfeed',
            name='tikedge_user',
            field=models.ForeignKey(blank=True, to='tasks.TikedgeUser', null=True),
        ),
        migrations.AddField(
            model_name='commentrecentuploads',
            name='challenge',
            field=models.ForeignKey(blank=True, to='social.Challenge', null=True),
        ),
        migrations.AddField(
            model_name='commentrecentuploads',
            name='tikedge_user',
            field=models.ForeignKey(blank=True, to='tasks.TikedgeUser', null=True),
        ),
        migrations.AddField(
            model_name='commentchallengeacceptance',
            name='challenge',
            field=models.ForeignKey(blank=True, to='social.Challenge', null=True),
        ),
        migrations.AddField(
            model_name='commentchallengeacceptance',
            name='tikedge_user',
            field=models.ForeignKey(blank=True, to='tasks.TikedgeUser', null=True),
        ),
        migrations.AddField(
            model_name='challengerating',
            name='challenge',
            field=models.ForeignKey(blank=True, to='social.Challenge', null=True),
        ),
        migrations.AddField(
            model_name='challengerating',
            name='tikedge_user',
            field=models.ForeignKey(blank=True, to='tasks.TikedgeUser', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='seenvideoset',
            unique_together=set([('tikedge_user', 'video_set')]),
        ),
        migrations.AlterUniqueTogether(
            name='seenrecentupload',
            unique_together=set([('tikedge_user', 'video')]),
        ),
        migrations.AlterUniqueTogether(
            name='seenchallenge',
            unique_together=set([('tikedge_user', 'challenge')]),
        ),
        migrations.AlterUniqueTogether(
            name='followchallenge',
            unique_together=set([('users', 'challenge')]),
        ),
    ]
