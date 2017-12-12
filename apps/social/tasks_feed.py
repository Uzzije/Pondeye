#!/usr/bin/python
"""
Feed and Notification Classes for Social News Feed of Application
"""
from models import ProfilePictures,\
    BuildCredMilestone, SeenMilestone, SeenPictureSet, SeenProject, VoucheProject, \
    Follow, ProgressImpressedCount,SeenProgress, ProjectVideo
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
        self.follow_count = self.follow()
        self.task_owner_name = self.get_name()
        self.is_picture_feed = self.is_picture_feed()
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
        if self.type_of_feed is global_variables.VIDEO_SET or self.type_of_feed is global_variables.RECENT_VIDEO_UPLOAD:
            return self.tasks.project.user
        else:
            return self.tasks.user

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
        if self.type_of_feed is global_variables.MILESTONE:
            print self.task_owner_name, " slammer"
            message = "Milestone: %s." % \
                      self.tasks.blurb
            return message
        elif self.type_of_feed is global_variables.PICTURE_SET:
            message = "For milestone: %s." % self.tasks.milestone.blurb
            return message
        elif self.type_of_feed is global_variables.PROJECT:
            message = "Goal: %s" % self.tasks.blurb
            return message
        elif self.type_of_feed is global_variables.PROGRESS:
            message =  "Goal: %s. Progress Highlights "% self.tasks.project.name_of_project
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
        try:
            if self.type_of_feed is global_variables.MILESTONE:
                seensd = SeenMilestone.objects.get(tasks=self.tasks)
            elif self.type_of_feed is global_variables.PICTURE_SET:
                seensd = SeenPictureSet.objects.get(tasks=self.tasks)
            elif self.type_of_feed is global_variables.PROJECT:
                seensd = SeenProject.objects.get(tasks=self.tasks)
            else:
                return 0
            count = seensd.users.count()
        except ObjectDoesNotExist:
            count = 0
        return count

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
        count = 0
        try:
            follows = Follow.objects.get(tasks=self.tasks)
            count = follows.users.count()
        except (ValueError, ObjectDoesNotExist):
            pass
        return count

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

    def project_video_url(self):
        try:
            video_url = ProjectVideo.objects.get(project=self.tasks)
        except ObjectDoesNotExist:
            return None
        return self.url_domain+video_url.url

# https://www.evernote.com/shard/s444/nl/2147483647/d9a542ad-437a-400d-aeb3-fbb7ed760dd9/
class ProgressFeed(PondFeed):

    def __init__(self, tasks, type_of_feed, url_domain=global_variables.CURRENT_URL, local_timezone='UTC'):
        PondFeed.__init__(self, tasks, type_of_feed, url_domain=url_domain)
        self.local_timezone = local_timezone
        self.progress = self.list_of_progress()

    def get_experience_with(self, progress):
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

    def list_of_progress(self):
        if self.tasks.is_empty:
            return None
        progress_list = []
        progress_dic = {}
        created_sec = int(self.created.strftime('%s'))
        for progress in self.tasks.list_of_progress_pictures.filter(is_deleted=False):
            progress_list.append({
               'name': self.task_owner_name,
               'progress_message': progress.name_of_progress,
               'seen_count': self.progress_seen_count(progress),
               'impress_count': self.impress_count(progress),
               'created':utc_to_local(progress.created, local_timezone=self.local_timezone).strftime("%B %d %Y %I:%M %p"),
               'id': progress.id,
               'image_url':self.get_image_url(progress),
               'experience_with':self.get_experience_with(progress)
            })
        if progress_list:
            progress_dic = {
                'created_sec':created_sec,
                'list_of_progress':progress_list,
                'created':utc_to_local(self.tasks.created, local_timezone=self.local_timezone).strftime("%B %d %Y %I:%M %p"),
                'message':self.message,
                'is_picture_feed': False,
                'is_milestone_feed': False,
                'is_project_feed': False,
                'is_progress_feed': True,
                'profile_url':self.profile_url,
                'id': self.tasks.project.id,
                'user_id':self.tasks.project.user.user.id,
                'progress_set_id': self.tasks.id,
                'name': self.task_owner_name,
            }
        return progress_dic

    def get_image_url(self, progress):
        return self.url_domain+progress.picture.url

    def impress_count(self, progress):
        impress_count = ProgressImpressedCount.objects.get(tasks=progress).get_count()
        return impress_count

    def progress_seen_count(self, progress):
        seen_count = SeenProgress.objects.get(tasks=progress).get_count()
        return seen_count


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
            'is_picture_feed': False,
            'is_milestone_feed': False,
            'is_recent_progress': True,
            'is_progress_set_feed': False,
            'profile_url':self.profile_url,
            'id': self.tasks.project.id,
            'user_id':self.tasks.project.user.user.id,
            'name': self.task_owner_name,
            'video_url':self.get_video_url(self.tasks)
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
                'is_picture_feed': False,
                'is_milestone_feed': False,
                'is_project_feed': False,
                'is_progress_set_feed': True,
                'profile_url':self.profile_url,
                'id': self.tasks.project.id,
                'user_id':self.tasks.project.user.user.id,
                'progress_set_id': self.tasks.id,
                'name': self.task_owner_name,
                'video_url':self.get_video_set_url(self.tasks)
            }
        return progress_dic

    def get_video_url(self, progress):
        return progress.video.url

    def get_video_set_url(self, progress_set):
        return progress_set.video_timeline.url

    def impress_count(self, progress):
        # impress_count = ProgressImpressedCount.objects.get(tasks=progress).get_count()
        return 0

    def progress_seen_count(self, progress):
        # seen_count = SeenProgress.objects.get(tasks=progress).get_count()
        return 0


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






