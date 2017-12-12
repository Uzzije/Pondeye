# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings
import image_cropping.fields


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
        ('friendship', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BuildCredMilestone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tasks', models.ForeignKey(blank=True, to='tasks.Milestone', null=True)),
                ('users', models.ManyToManyField(to='tasks.TikedgeUser', verbose_name='User That Milestone Owner Built Cred For')),
            ],
        ),
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('latest_follow', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_video_tasks', models.BooleanField(default=False)),
                ('is_picture_tasks', models.BooleanField(default=True)),
                ('tasks', models.ForeignKey(blank=True, to='tasks.UserProject', null=True)),
                ('users', models.ManyToManyField(to='tasks.TikedgeUser', verbose_name='users that follow/interested in a project')),
            ],
        ),
        migrations.CreateModel(
            name='Friends',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('friends', models.ManyToManyField(related_name='user_friends', to='tasks.TikedgeUser')),
                ('user', models.ForeignKey(blank=True, to='tasks.TikedgeUser', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='JournalComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.CharField(default=None, max_length=2000)),
                ('is_deleted', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='JournalPost',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('entry_blurb', models.CharField(default=None, max_length=240)),
                ('day_entry', models.IntegerField(default=1)),
                ('day_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('event_type', models.CharField(default=b'np', max_length=20)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_picture_set', models.BooleanField(default=False)),
                ('is_milestone_entry', models.BooleanField(default=False)),
                ('is_project_entry', models.BooleanField(default=False)),
                ('slug', models.SlugField(default=None, max_length=100)),
                ('milestone_entry', models.ForeignKey(to='tasks.Milestone', null=True)),
                ('new_project_entry', models.ForeignKey(to='tasks.UserProject', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LetDownMilestone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('latest_letDown', models.DateTimeField(default=django.utils.timezone.now)),
                ('tasks', models.ForeignKey(blank=True, to='tasks.Milestone', null=True)),
                ('users', models.ManyToManyField(to='tasks.TikedgeUser', verbose_name='users that were let down by vouche for your Milestone')),
            ],
        ),
        migrations.CreateModel(
            name='LetDownProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('latest_letDown', models.DateTimeField(default=django.utils.timezone.now)),
                ('tasks', models.ForeignKey(blank=True, to='tasks.UserProject', null=True)),
                ('users', models.ManyToManyField(to='tasks.TikedgeUser', verbose_name='users that were let down by vouche for your Goal')),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type_of_notification', models.CharField(max_length=100)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('read', models.BooleanField(default=False)),
                ('name_of_notification', models.TextField(default='', max_length=700)),
                ('id_of_object', models.IntegerField(default=0)),
                ('date_read', models.DateTimeField(null=True, blank=True)),
                ('friend_request', models.ForeignKey(blank=True, to='friendship.FriendshipRequest', null=True)),
                ('project_update', models.ForeignKey(blank=True, to='tasks.UserProject', null=True)),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Picture',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image_name', models.CharField(max_length=300)),
                ('milestone_pics', models.ImageField(upload_to='image/tasks/%Y/%m/%d', verbose_name='profile image')),
                (b'cropping', image_cropping.fields.ImageRatioField('milestone_pics', '5x5', hide_image_field=False, size_warning=False, allow_fullsize=False, free_crop=False, adapt_rotation=False, help_text=None, verbose_name='cropping')),
                ('date_uploaded', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_edited', models.DateTimeField(null=True, blank=True)),
                ('is_before', models.BooleanField(default=True)),
                ('tikedge_user', models.ForeignKey(blank=True, to='tasks.TikedgeUser', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PictureSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('last_updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('after_picture', models.ForeignKey(related_name='after_picture', blank=True, to='social.Picture', null=True)),
                ('before_picture', models.ForeignKey(related_name='before_picture', blank=True, to='social.Picture', null=True)),
                ('milestone', models.ForeignKey(blank=True, to='tasks.Milestone', null=True)),
                ('tikedge_user', models.ForeignKey(blank=True, to='tasks.TikedgeUser', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Pond',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_of_pond', models.CharField(max_length=250)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_deleted', models.DateTimeField(null=True, blank=True)),
                ('slug', models.SlugField(default=None, max_length=100)),
                ('purpose', models.CharField(default=None, max_length=110)),
                ('blurb', models.CharField(default=None, max_length=51)),
                ('is_deleted', models.BooleanField(default=False)),
                ('pond_creator', models.ForeignKey(related_name='pond_creater', blank=True, to='tasks.TikedgeUser', null=True)),
                ('pond_members', models.ManyToManyField(related_name='pond_member', to='tasks.TikedgeUser')),
                ('tags', models.ManyToManyField(to='tasks.TagNames')),
            ],
        ),
        migrations.CreateModel(
            name='PondMembership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_removed', models.DateTimeField(null=True, blank=True)),
                ('pond', models.ForeignKey(blank=True, to='social.Pond', null=True)),
                ('user', models.ForeignKey(blank=True, to='tasks.TikedgeUser', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PondProgressFeed',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_of_feed', models.TextField(default=None)),
                ('is_picture_feed', models.BooleanField(default=True)),
                ('is_video_feed', models.BooleanField(default=False)),
                ('pond', models.ForeignKey(to='social.Pond', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PondRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_requested', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_response', models.DateTimeField(null=True, blank=True)),
                ('request_accepted', models.BooleanField(default=False)),
                ('request_denied', models.BooleanField(default=False)),
                ('request_responded_to', models.BooleanField(default=False)),
                ('member_that_responded', models.ForeignKey(related_name='the_member_that_responded', blank=True, to='tasks.TikedgeUser', null=True)),
                ('pond', models.ForeignKey(blank=True, to='social.Pond', null=True)),
                ('user', models.ForeignKey(blank=True, to='tasks.TikedgeUser', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PondSpecificProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pond', models.ManyToManyField(to='social.Pond')),
                ('project', models.ForeignKey(blank=True, to='tasks.UserProject', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProfilePictures',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image_name', models.CharField(max_length=100)),
                ('profile_pics', models.ImageField(upload_to='image/%Y/%m/%d', verbose_name='profile image')),
                (b'cropping', image_cropping.fields.ImageRatioField('profile_pics', '5x5', hide_image_field=False, size_warning=False, allow_fullsize=False, free_crop=False, adapt_rotation=False, help_text=None, verbose_name='cropping')),
                ('date_uploaded', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_deleted', models.BooleanField(default=False)),
                ('tikedge_user', models.ForeignKey(blank=True, to='tasks.TikedgeUser', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProgressImpressedCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('latest_impressed', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_video_tasks', models.BooleanField(default=False)),
                ('is_picture_tasks', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProgressPicture',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image_name', models.TextField(max_length=600)),
                ('picture', models.ImageField(upload_to='image/progresspicture/%Y/%m/%d', verbose_name='progress image')),
                ('name_of_progress', models.TextField(max_length=600, null=True, blank=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('last_updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('blurb', models.CharField(default=None, max_length=150)),
                ('experience_with', models.ManyToManyField(default=None, to='tasks.TikedgeUser')),
            ],
        ),
        migrations.CreateModel(
            name='ProgressPictureSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('last_updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_empty', models.BooleanField(default=True)),
                ('list_of_progress_pictures', models.ManyToManyField(to='social.ProgressPicture')),
                ('project', models.ForeignKey(blank=True, to='tasks.UserProject', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProgressVideo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('video_name', models.TextField(max_length=600)),
                ('video', models.FileField(upload_to='video/progressvideo/%Y/%m/%d', verbose_name='progress video')),
                ('name_of_progress', models.TextField(max_length=600, null=True, blank=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('last_updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('blurb', models.CharField(default=None, max_length=150)),
                ('experience_with', models.ManyToManyField(default=None, to='tasks.TikedgeUser')),
            ],
        ),
        migrations.CreateModel(
            name='ProgressVideoSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('last_updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_empty', models.BooleanField(default=True)),
                ('video_timeline', models.FileField(default=None, upload_to='video/progress-timeline-video/%Y/%m/%d', verbose_name='progress video')),
                ('list_of_progress_videos', models.ManyToManyField(to='social.ProgressVideo')),
                ('project', models.ForeignKey(blank=True, to='tasks.UserProject', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectPicture',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image_name', models.CharField(max_length=300)),
                ('date_uploaded', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_edited', models.DateTimeField(null=True, blank=True)),
                ('is_before', models.BooleanField(default=True)),
                ('picture', models.ImageField(upload_to='image/tasks/%Y/%m/%d', verbose_name='profile image')),
                ('is_deleted', models.BooleanField(default=False)),
                ('project', models.ForeignKey(blank=True, to='tasks.UserProject', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectVideo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('video_name', models.CharField(max_length=300)),
                ('date_uploaded', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_edited', models.DateTimeField(null=True, blank=True)),
                ('video', models.FileField(upload_to='image/tasks/%Y/%m/%d', verbose_name='profile image')),
                ('is_deleted', models.BooleanField(default=False)),
                ('project', models.ForeignKey(blank=True, to='tasks.UserProject', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SeenMilestone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tasks', models.ForeignKey(blank=True, to='tasks.Milestone', null=True)),
                ('users', models.ManyToManyField(to='tasks.TikedgeUser', verbose_name='Users That saw the milestones')),
            ],
        ),
        migrations.CreateModel(
            name='SeenPictureSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tasks', models.ForeignKey(blank=True, to='social.PictureSet', null=True)),
                ('users', models.ManyToManyField(to='tasks.TikedgeUser', verbose_name='Users That saw the pictureSet')),
            ],
        ),
        migrations.CreateModel(
            name='SeenProgress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_video_tasks', models.BooleanField(default=False)),
                ('is_picture_tasks', models.BooleanField(default=True)),
                ('tasks', models.ForeignKey(blank=True, to='social.ProgressPicture', null=True)),
                ('users', models.ManyToManyField(to='tasks.TikedgeUser', verbose_name='Users That saw the pictureSet')),
                ('video_tasks', models.ForeignKey(blank=True, to='social.ProgressVideo', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SeenProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tasks', models.ForeignKey(blank=True, to='tasks.UserProject', null=True)),
                ('users', models.ManyToManyField(to='tasks.TikedgeUser', verbose_name='Users That saw the projects')),
            ],
        ),
        migrations.CreateModel(
            name='ShoutOutEmailAndNumber',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_email_or_num', models.TextField(default=None)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_email', models.BooleanField(default=False)),
                ('is_number', models.BooleanField(default=True)),
                ('is_video_shout_outs', models.BooleanField(default=False)),
                ('is_picture_shout_outs', models.BooleanField(default=True)),
                ('email_or_text_sent', models.BooleanField(default=False)),
                ('sent_date', models.DateTimeField(null=True, blank=True)),
                ('user_responded', models.BooleanField(default=False)),
                ('date_of_response', models.DateTimeField(null=True, blank=True)),
                ('type_of_response', models.CharField(default='noResponse', max_length=250, verbose_name='user can respond by joining or not joining pondeye')),
                ('progress_picture', models.ForeignKey(blank=True, to='social.ProgressPicture', null=True)),
                ('progress_video', models.ForeignKey(blank=True, to='social.ProgressVideo', null=True)),
                ('tikedge_user', models.ForeignKey(verbose_name='User that requested the shoutout', to='tasks.TikedgeUser')),
            ],
        ),
        migrations.CreateModel(
            name='VoucheMilestone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('latest_vouch', models.DateTimeField(default=django.utils.timezone.now)),
                ('tasks', models.ForeignKey(blank=True, to='tasks.Milestone', null=True)),
                ('users', models.ManyToManyField(to='tasks.TikedgeUser', verbose_name='User That Vouche For the milestone')),
            ],
        ),
        migrations.CreateModel(
            name='VoucheProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('latest_vouch', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_video_tasks', models.BooleanField(default=False)),
                ('is_picture_tasks', models.BooleanField(default=True)),
                ('tasks', models.ForeignKey(blank=True, to='tasks.UserProject', null=True)),
                ('users', models.ManyToManyField(to='tasks.TikedgeUser', verbose_name='User That Vouche For the milestone')),
                ('video_tasks', models.ForeignKey(blank=True, to='social.ProgressVideo', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='WorkEthicRank',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('consistency_rank', models.IntegerField(default=0)),
                ('correct_vouching_rank', models.IntegerField(default=0)),
                ('work_ethic_rank', models.IntegerField(default=0)),
                ('tikedge_user', models.ForeignKey(blank=True, to='tasks.TikedgeUser', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='progressimpressedcount',
            name='tasks',
            field=models.ForeignKey(blank=True, to='social.ProgressPicture', null=True),
        ),
        migrations.AddField(
            model_name='progressimpressedcount',
            name='users',
            field=models.ManyToManyField(to='tasks.TikedgeUser', verbose_name='Users That saw the pictureSet'),
        ),
        migrations.AddField(
            model_name='progressimpressedcount',
            name='video_tasks',
            field=models.ForeignKey(blank=True, to='social.ProgressVideo', null=True),
        ),
        migrations.AddField(
            model_name='pondprogressfeed',
            name='progress_picture',
            field=models.ForeignKey(related_name='picture_pond_feed', blank=True, to='social.ProgressPicture', null=True),
        ),
        migrations.AddField(
            model_name='pondprogressfeed',
            name='progress_video',
            field=models.ForeignKey(related_name='video_pond_feed', blank=True, to='social.ProgressVideo', null=True),
        ),
        migrations.AddField(
            model_name='pondprogressfeed',
            name='project',
            field=models.ForeignKey(related_name='project_pond_feed', to='tasks.UserProject', null=True),
        ),
        migrations.AddField(
            model_name='journalpost',
            name='picture_set_entry',
            field=models.ForeignKey(to='social.PictureSet', null=True),
        ),
        migrations.AddField(
            model_name='journalpost',
            name='user',
            field=models.ForeignKey(to='tasks.TikedgeUser', null=True),
        ),
        migrations.AddField(
            model_name='journalcomment',
            name='journal_post',
            field=models.ForeignKey(to='social.JournalPost', null=True),
        ),
        migrations.AddField(
            model_name='follow',
            name='video_tasks',
            field=models.ForeignKey(blank=True, to='social.ProgressVideo', null=True),
        ),
    ]
