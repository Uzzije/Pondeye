#!/usr/bin/python
"""
Feed and Notification Classes for Social News Feed of Application
"""
from models import ProfilePictures,\
    BuildCredMilestone, VoucheProject, \
    FollowChallenge, SeenChallenge, ChallengeVideo, \
    CommentChallengeAcceptance, CommentRecentUploads, CommentRequestFeed, SeenVideoSet, SeenRecentUpload, \
    ChallengeRating, HighlightImpressedCount, RecentUploadImpressedCount
from friendship.models import FriendshipRequest
from django.db.models import Q
import global_variables
from ..tasks.modules import utc_to_local
from django.core.exceptions import ObjectDoesNotExist


class PondFeed:

    def __init__(self, tasks, type_of_feed, url_domain=global_variables.CURRENT_URL):
        self.tasks = tasks
        self.type_of_feed = type_of_feed
        self.url_domain = url_domain
        self.tikedge_user = self.get_user_tikedge()
        self.seen_count = self.seens()
        self.vouche_count = self.vouche()
        self.task_owner_name = self.get_name()
        self.is_project_feed = self.is_project_feed()
        self.is_progress_feed = self.is_progress_feed()
        self.message = self.message()
        self.before_url = self.get_before_url()
        self.after_url = self.get_after_url()
        self.feed_id = self.tasks.id
        self.created = self.get_date_created()
        self.profile_url = self.task_owner_profile_pic_url()
        self.feed_user = self.get_user_tikedge().user

    def get_user_tikedge(self):
        if self.type_of_feed is global_variables.VIDEO_SET:
            return self.tasks.challenge.project.user
        elif self.type_of_feed is global_variables.RECENT_VIDEO_UPLOAD:
            return self.tasks.challenge.project.user
        else:
            return self.tasks.project.user

    def is_progress_feed(self):
        if self.type_of_feed is global_variables.PROGRESS:
            return True
        else:
            return False

    def is_picture_feed(self):
        if self.type_of_feed is global_variables.PICTURE_SET:
            print " Lets get this going here ",
            return True
        else:
            return False

    def is_project_feed(self):
        if self.type_of_feed is global_variables.PROJECT:
            return True
        else:
            return False

    def message(self):
        if self.type_of_feed is global_variables.VIDEO_SET:
            message = self.tasks.challenge.project.blurb
            return message
        elif self.type_of_feed is global_variables.RECENT_VIDEO_UPLOAD:
            message = self.tasks.blurb
            return message
        elif self.type_of_feed is global_variables.CHALLENGED_ACCEPTED:
            message = self.tasks.project.blurb
            return message
        elif self.type_of_feed is global_variables.CHALLENGED_BY_SOMEONE:
            message =  self.tasks.project.blurb
            return message
        else:
            return None

    def get_date_created(self):
        if self.type_of_feed is global_variables.MILESTONE:
            return self.tasks.last_update
        elif self.type_of_feed is global_variables.PICTURE_SET:
            return self.tasks.after_picture.date_uploaded
        elif self.type_of_feed is global_variables.VIDEO_SET or self.type_of_feed is global_variables.RECENT_VIDEO_UPLOAD:
            return self.tasks.last_updated
        elif self.type_of_feed is global_variables.CHALLENGED_ACCEPTED:
            return self.tasks.date_responded
        elif self.type_of_feed is global_variables.CHALLENGED_BY_SOMEONE:
            return self.tasks.created
        else:
            return self.tasks.last_update #it is a project feed

    def get_before_url(self):
        if self.type_of_feed is global_variables.PICTURE_SET:
            return self.url_domain+self.tasks.before_picture.milestone_pics.url
        else:
            return None

    def get_after_url(self):
        if self.type_of_feed is global_variables.PICTURE_SET:
            return self.url_domain+self.tasks.after_picture.milestone_pics.url
        else:
            return None

    def seens(self):
        if self.type_of_feed is global_variables.VIDEO_SET:
            seensd = SeenVideoSet.objects.filter(video_set=self.tasks)
            return seensd.count()
        elif self.type_of_feed is global_variables.RECENT_VIDEO_UPLOAD:
            seensd = SeenRecentUpload.objects.filter(video=self.tasks)
            return seensd.count()
        elif self.type_of_feed is global_variables.CHALLENGED_ACCEPTED or \
                        self.type_of_feed is global_variables.CHALLENGED_BY_SOMEONE:
            seensd = SeenChallenge.objects.filter(challenge=self.tasks)
            return seensd.count()
        return 0

    def challenge_rating(self):
        """
        Users grade how hard this challenge is.
        :return:
        """
        if self.type_of_feed is global_variables.VIDEO_SET:
            ch_rating = ChallengeRating.objects.filter(challenge=self.tasks.challenge).values_list('number', flat=True)
        elif self.type_of_feed is global_variables.RECENT_VIDEO_UPLOAD:
            ch_rating = ChallengeRating.objects.filter(challenge=self.tasks.challenge).values_list('number', flat=True)
        elif self.type_of_feed is global_variables.CHALLENGED_ACCEPTED or \
                        self.type_of_feed is global_variables.CHALLENGED_BY_SOMEONE:
            ch_rating = ChallengeRating.objects.filter(challenge=self.tasks).values_list('number', flat=True)
        else:
            ch_rating = []
        average = float(sum(ch_rating)) / max(len(ch_rating), 1)
        return average

    def get_start_time(self):
        return self.tasks.start

    def get_end_time(self):
        return self.tasks.end

    def get_name_of_tasks(self):
        try:
            return self.tasks.name_of_tasks+ " from " + self.get_start_time().strftime("%B %d %Y %I:%M %p") \
                   + " to " + self.get_end_time().strftime("%B %d %Y %I:%M %p")
        except (KeyError, AttributeError):
            return None

    def vouche(self):
        try:
            vouched = VoucheProject.objects.get(tasks=self.tasks)
            count = vouched.get_count()
        except (ObjectDoesNotExist, AttributeError, ValueError):
            count = 0
        return count

    def build_cred(self):
        try:
            buildCred = BuildCredMilestone.objects.get(tasks=self.tasks)
            count = buildCred.users.count()
        except (ObjectDoesNotExist, AttributeError, ValueError):
            count = 0
        return count

    def follow(self):
        if self.type_of_feed is global_variables.VIDEO_SET or self.type_of_feed is global_variables.RECENT_VIDEO_UPLOAD:
            follows = FollowChallenge.objects.filter(challenge=self.tasks.challenge)
        else:
            follows = FollowChallenge.objects.filter(challenge=self.tasks)
        return follows.count()

    def impress_count(self):
        if self.type_of_feed is global_variables.RECENT_VIDEO_UPLOAD:
            seens = RecentUploadImpressedCount.objects.filter(progress=self.tasks).count()
            return seens
        if self.type_of_feed is global_variables.VIDEO_SET:
            seens = HighlightImpressedCount.objects.filter(progress_set=self.tasks).count()
            return seens
        return 0

    def comments(self, timezone):
        comments_list = []
        if self.type_of_feed is global_variables.VIDEO_SET or self.type_of_feed is global_variables.RECENT_VIDEO_UPLOAD:
            comments = CommentChallengeAcceptance.objects.filter(challenge=self.tasks.challenge).order_by('-created')
        elif self.type_of_feed is global_variables.CHALLENGED_ACCEPTED:
            comments = CommentRecentUploads.objects.filter(recent_upload=self.tasks).order_by('-created')
        else:
            comments = CommentRequestFeed.objects.filter(challenge=self.tasks).order_by('-created')
        for comm in comments:
            com_dic = {
                'first_name':comm.tikedge_user.user.first_name,
                'last_name':comm.tikedge_user.user.last_name,
                'comment':comm.comment,
                'date': utc_to_local(comm.created, local_timezone=timezone).strftime("%B %d %Y %I:%M %p"),
                'id':comm.id
            }
            comments_list.append(com_dic)
        return comments_list

    def get_name(self):
        try:
            print '%s %s from feed' % (self.tasks.user.user.first_name, self.tasks.user.user.last_name)
            name = '%s' % self.tasks.user.user.first_name + " " + self.tasks.user.user.last_name
            return name
        except (AttributeError, ValueError):
            try:
                name = '%s' % self.tikedge_user.user.first_name + " " + self.tikedge_user.user.last_name
            except (AttributeError, ValueError):
                try:
                    name = '%s' % self.tasks.project.user.user.first_name + " " + self.tasks.project.user.user.last_name
                except (AttributeError, ValueError):
                    return None
        return name

    def task_owner_profile_pic_url(self):
        try:
            profile_picture = ProfilePictures.objects.get(tikedge_user=self.tikedge_user)
            return self.url_domain+profile_picture.profile_pics.url
        except (AttributeError, ValueError, ObjectDoesNotExist):
            return None


class ChallengeFeed(PondFeed):

    def __init__(self, tasks, type_of_feed, url_domain=global_variables.CURRENT_URL, local_timezone='UTC'):
        PondFeed.__init__(self, tasks, type_of_feed, url_domain=url_domain)
        self.local_timezone = local_timezone
        self.has_video = False
        self.challenger_fn = self.tasks.challenger.user.first_name
        self.challenger_ln = self.tasks.challenger.user.last_name
        self.challenged_fn = self.tasks.challenged.user.first_name
        self.challenged_ln = self.tasks.challenged.user.last_name
        self.challenged_id = self.tasks.challenged.user.id
        self.challenger_id = self.tasks.challenger.user.id

    def progress(self):
        created_sec = int(self.created.strftime('%s'))
        progress_dic = {
            'ch_rating': self.challenge_rating(),
            'challenge_blurb':self.message,
            'challenge':self.tasks.project.name_of_project,
            'challenger_fn':self.challenger_fn,
            'challenger_ln':self.challenger_ln,
            'challenged_fn':self.challenged_fn,
            'challenged_ln':self.challenged_ln,
            'comments': self.comments(self.local_timezone),
            'comments_count': len(self.comments(self.local_timezone)),
            'seen': self.seens(),
            'follow': self.follow(),
            'has_video': self.has_video,
            'video_url': self.get_challenge_video_url(self.tasks),
            'created_sec':created_sec,
            'is_challenge_accept': False,
            'is_challenge_req': False,
            'is_recent_progress': False,
            'is_video_highlight': False,
            'created':utc_to_local(self.tasks.created, local_timezone=self.local_timezone).strftime("%B %d %Y %I:%M %p"),
            'name': self.task_owner_name,
            'profile_url':self.profile_url,
            'id':self.tasks.project.id
        }
        return progress_dic

    def get_challenge_video_url(self, tasks):
        try:
            cv_cd = ChallengeVideo.objects.get(challenge=self.tasks)
            self.has_video = True
        except ObjectDoesNotExist:
            cv_cd = ""
        return cv_cd


class RequestFeed(ChallengeFeed):

    def __init__(self, tasks, url_domain=global_variables.CURRENT_URL, local_timezone='UTC'):
        ChallengeFeed.__init__(self, tasks, global_variables.CHALLENGED_BY_SOMEONE, url_domain=url_domain)

    def progress(self):
        progress_dic = ChallengeFeed.progress(self)
        progress_dic['is_challenge_req'] = True
        return progress_dic


class AcceptanceFeed(ChallengeFeed):

    def __init__(self, tasks, url_domain=global_variables.CURRENT_URL, local_timezone='UTC'):
        ChallengeFeed.__init__(self, tasks, global_variables.CHALLENGED_ACCEPTED, url_domain=url_domain)
        self.local_timezone = local_timezone

    def progress(self):
        progress_dic = ChallengeFeed.progress(self)
        progress_dic['is_challenge_accept'] = True
        return progress_dic

# https://www.evernote.com/shard/s444/nl/2147483647/d9a542ad-437a-400d-aeb3-fbb7ed760dd9/


class VideoProgressFeed(PondFeed):

    def __init__(self, tasks, type_of_feed, url_domain=global_variables.CURRENT_URL, local_timezone='UTC'):
        PondFeed.__init__(self, tasks, type_of_feed, url_domain=url_domain)
        self.local_timezone = local_timezone
        self.progress = self.progress_feed()

    def get_experience_with(self, progress):
        """
        Get Experience with tikedge users for progress model.
        :param progress:
        :return:
        """
        list_of_tikedge_users = []
        for each_user in progress.experience_with.all():
            list_of_tikedge_users.append({
                'first_name': each_user.user.first_name,
                'last_name': each_user.user.last_name,
                'id': each_user.user.id,
                'user_name':each_user.user.username
            })
        if not list_of_tikedge_users:
            return False
        return list_of_tikedge_users

    def progress_feed(self):
        if self.type_of_feed == global_variables.VIDEO_SET:
            return self.videos_highlight()
        else:
            return self.recent_upload()

    def recent_upload(self):
        created_sec = int(self.created.strftime('%s'))
        progress_dic = {
            'created_sec':created_sec,
            'created':utc_to_local(self.tasks.created, local_timezone=self.local_timezone).strftime("%B %d %Y %I:%M %p"),
            'message':self.message,
            'is_challenge_accept': False,
            'is_challenge_req': False,
            'is_recent_progress': True,
            'is_video_highlight': False,
            'profile_url':self.profile_url,
            'id': self.tasks.challenge.id,
            'user_id':self.tasks.challenge.project.user.user.id,
            'name': self.task_owner_name,
            'video_url':self.get_video_url(self.tasks),
            'comments': self.comments(self.local_timezone),
            'seen': self.seens(),
            'follow': self.follow(),
            'impressed': self.impress_count(),
            'progress_id': self.tasks.id
        }
        return progress_dic

    def videos_highlight(self):
        """
        Return a list of progress videos from VideoProgressSet
        :return:
        """
        if self.tasks.is_empty:
            return None
        progress_dic = {}
        created_sec = int(self.created.strftime('%s'))
        progress_query_set = self.tasks.list_of_progress_videos.filter(is_deleted=False).order_by('-created')
        if progress_query_set:
            progress_dic = {
                'created_sec':created_sec,
                'created':utc_to_local(self.tasks.created, local_timezone=self.local_timezone).strftime("%B %d %Y %I:%M %p"),
                'message':self.message,
                'is_challenge_accept': False,
                'is_challenge_req': False,
                'is_recent_progress': False,
                'is_video_highlight': True,
                'profile_url':self.profile_url,
                'id': self.tasks.challenge.project.id,
                'user_id':self.tasks.challenge.project.user.user.id,
                'progress_set_id': self.tasks.id,
                'name': self.task_owner_name,
                'video_url':self.get_video_set_url(self.tasks),
                'comments': self.comments(self.local_timezone),
                'seen': self.seens(),
                'follow': self.follow(),
                'impressed': self.impress_count(),
            }
        return progress_dic

    def get_video_url(self, progress):
        return progress.video.url

    def get_video_set_url(self, progress_set):
        return progress_set.video_timeline.url


class NotificationFeed:

    def __init__(self, user, notifications):
        self.user = user
        self.user_pk = user.pk
        self.notification = notifications

    def friend_request_notifications(self):
        friend_requests = FriendshipRequest.objects.filter(pk=self.user_pk)
        return friend_requests

    def get_unread_notification(self):
        notification_list = []
        unread_notify = self.notification.filter(Q(read=False)).order_by('created')
        for each_notif in unread_notify:
            new_object = SingleNotification(each_notif)
            notification_list.append(new_object)
        return notification_list

    def highlight_new_notification(self):
        unread_notify = self.notification.filter(Q(read=False)).order_by('created')
        '''
        pond_request = False
        pond_request_accepted = False
        new_ponder = False
        interested = False
        let_down = False
        milestone_vouch = False
        milestone_failed = False
        project_failed = False
        '''
        has_notification = False
        list_of_notifications = []
        if unread_notify:
            has_notification = True
        for each_notif in unread_notify:
            list_of_notifications.append(each_notif.name_of_notification)

            '''
            if each_notif.type_of_notification == global_variables.POND_REQUEST:

                list_of_notifications.append(each_notif.name_of_notification)
            if each_notif.type_of_notification == global_variables.POND_REQUEST_ACCEPTED:
                has_notification = True

            if each_notif.type_of_notification == global_variables.NEW_PONDERS:
                has_notification = True
                new_ponder = True
            if each_notif.type_of_notification == global_variables.NEW_PROJECT_INTERESTED:
                has_notification = True
                interested = True
            if each_notif.type_of_notification == global_variables.NEW_PROJECT_LETDOWN:
                has_notification = True
                let_down = "One of the goals your were following wasn't completed"
            if each_notif.type_of_notification == global_variables.NEW_PROJECT_VOUCH:
                has_notification = True
                project_vouch = each_notif.name_of_notification
            if each_notif.type_of_notification == global_variables.USER_DELETED_MILESTONE:
                has_notification = True
                milestone_failed =  each_notif.name_of_notification
            if each_notif.type_of_notification == global_variables.USER_DELETED_PROJECT:
                has_notification =  each_notif.name_of_notification
                project_failed =  each_notif.name_of_notification
            '''
        notification_dic = {
            'has_notification':has_notification,
            'notifications':list_of_notifications,
        }
        return notification_dic


class SingleNotification:

    def __init__(self, notification_object):
        self.notif = notification_object
        self.name = self.get_name()

    def get_name(self):

        if self.notif.name_of_notification != "":
            print "I am already made"
            return self.notif.name_of_notification
        if self.notif.type_of_notification == global_variables.FRIEND_REQUEST:
            name = "You have a new friend Request"
        elif self.notif.type_of_notification == global_variables.REQUEST_ACCEPTED:
            name = "Your Friend Request Has Been Accepted"
        elif self.notif.type_of_notification == global_variables.REQUEST_REJECTED:
            name = "Your Friend Request Has Been Rejected"
        else:
            name = "New Notification"
        self.notif.name_of_notification = name
        self.notif.save()
        return name






