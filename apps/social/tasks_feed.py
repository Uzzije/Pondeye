#!/usr/bin/python
"""
Feed and Notification Classes for Social News Feed of Application
"""
from models import Seen, Vouche, BuildCred, Follow, LetDown, ProfilePictures, Graded, \
BuildCredMilestone, SeenMilestone, SeenPictureSet, SeenProject, LetDownMilestone, VoucheMilestone
from ..tasks.models import TikedgeUser
from friendship.models import FriendshipRequest
from django.db.models import Q
import global_variables
from django.core.exceptions import ObjectDoesNotExist


class TasksFeed:

    def __init__(self, tasks):
        self.tasks = tasks
        self.seen_count = self.seens()
        self.vouche_count = self.vouche()
        self.build_cred_count = self.build_cred()
        self.follow_count = self.follow()
        self.letDown_count = self.letDown()
        self.name_of_task = self.get_name_of_tasks()
        self.id = tasks.id
        self.type_of_feed = global_variables.NEW_TASK_FEED
        self.created = self.get_start_time()
        self.task_owner_name = self.get_name()
        self.task_owner_profile_pic_url = self.task_owner_profile_pic_url()

    def seens(self):
        try:
            seensd = Seen.objects.get(tasks=self.tasks)
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
            vouched = Vouche.objects.get(tasks=self.tasks)
            count = vouched.users.count()
        except (ObjectDoesNotExist, AttributeError):
            count = 0
        return count

    def build_cred(self):
        try:
            buildCred = BuildCred.objects.get(tasks=self.tasks)
            count = buildCred.users.count()
        except (ObjectDoesNotExist, AttributeError):
            count = 0
        return count

    def follow(self):
        count = 0
        try:
            if self.tasks.part_of_project:
                try:
                    follows = Follow.objects.get(tasks=self.tasks.project)
                    count = follows.users.count()
                except ObjectDoesNotExist:
                    pass
        except AttributeError:
            pass
        return count

    def letDown(self):
        try:
            let_down = LetDown.objects.get(tasks=self.tasks)
            count = let_down.users.count()
        except (ObjectDoesNotExist, AttributeError):
            count = 0
        return count

    def get_name(self):
        try:
            print '%s %s from feed' % (self.tasks.user.user.first_name, self.tasks.user.user.last_name)
            return '%s %s' % (self.tasks.user.user.first_name, self.tasks.user.user.last_name)
        except AttributeError:
            return None

    def task_owner_profile_pic_url(self):
        try:
            profile_picture = ProfilePictures.objects.get(tikedge_user=self.tasks.user)
            return profile_picture.profile_pics.url
        except (AttributeError, ObjectDoesNotExist):
            return None


class PondFeed:

    def __init__(self, tasks, type_of_feed):
        self.tasks = tasks
        self.type_of_feed = type_of_feed
        self.seen_count = self.seens()
        self.vouche_count = self.vouche()
        #self.build_cred_count = self.build_cred()
        self.follow_count = self.follow()
        #self.letDown_count = self.letDown()
        #self.name_of_task = self.get_name_of_tasks()
        #self.id = tasks.id
        #self.created = self.get_start_time()
        self.task_owner_name = self.get_name()
        #self.task_owner_profile_pic_url = self.task_owner_profile_pic_url()
        self.is_milestone_feed = self.is_milestone_feed()
        self.is_picture_feed = self.is_picture_feed()
        self.is_project_feed = self.is_project_feed()
        self.message = self.message()
        self.before_url = self.get_before_url()
        self.after_url = self.get_after_url()
        self.feed_id = self.tasks.id
        self.created = self.get_date_created()

    def is_milestone_feed(self):
        if self.type_of_feed is global_variables.MILESTONE:
            return True
        else:
            return False

    def is_picture_feed(self):
        if self.type_of_feed is global_variables.PICTURE_SET:
            return True
        else:
            return False

    def is_project_feed(self):
        if self.type_of_feed is global_variables.NEW_PROJECT:
            return True
        else:
            return False

    def message(self):
        if self.type_of_feed is global_variables.MILESTONE:
            print self.task_owner_name, " slammer"
            message = "%s created a new milestone: %s for project: %s" % \
                      (self.task_owner_name, self.tasks.name_of_milestone, self.tasks.project.blurb)
            return message
        elif self.type_of_feed is global_variables.PICTURE_SET:
            message = "%s entered a journal entry for milestone: %s" % (self.task_owner_name,
                                                                        self.tasks.milestone.blurb)
            return message
        elif self.type_of_feed is global_variables.NEW_PROJECT:
            message = "%s created a new project: %s" % (self.task_owner_name, self.tasks.blurb)
            return message
        else:
            return None

    def get_date_created(self):
        if self.type_of_feed is global_variables.MILESTONE:
            return self.tasks.created_date
        elif self.type_of_feed is global_variables.PICTURE_SET:
            return self.tasks.after_picture.date_uploaded
        else:
            return self.tasks.made_live

    def get_before_url(self):
        if self.type_of_feed is global_variables.PICTURE_SET:
            return self.tasks.before_picture.milestone_pics.url
        else:
            return None

    def get_after_url(self):
        if self.type_of_feed is global_variables.PICTURE_SET:
            return self.tasks.after_picture.milestone_pics.url
        else:
            return None

    def seens(self):
        try:
            if self.type_of_feed is global_variables.MILESTONE:
                seensd = SeenMilestone.objects.get(tasks=self.tasks)
            elif self.type_of_feed is global_variables.PICTURE_SET:
                seensd = SeenPictureSet.objects.get(tasks=self.tasks)
            elif self.type_of_feed is global_variables.NEW_PROJECT:
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
            vouched = VoucheMilestone.objects.get(tasks=self.tasks)
            count = vouched.users.count()
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

    def letDown(self):
        try:
            let_down = LetDown.objects.get(tasks=self.tasks)
            count = let_down.users.count()
        except (ObjectDoesNotExist, AttributeError, ValueError):
            count = 0
        return count

    def get_name(self):
        try:
            print '%s %s from feed' % (self.tasks.user.user.first_name, self.tasks.user.user.last_name)
            name = '%s' % self.tasks.user.user.first_name + " " + self.tasks.user.user.last_name
            return name
        except (AttributeError, ValueError):
            try:
                name = '%s' % self.tasks.tikedge_user.user.first_name + " " + self.tasks.tikedge_user.user.last_name
            except (AttributeError, ValueError):
                return None
        return name

    def task_owner_profile_pic_url(self):
        try:
            profile_picture = ProfilePictures.objects.get(tikedge_user=self.tasks.user)
            return profile_picture.profile_pics.url
        except (AttributeError, ObjectDoesNotExist):
            return None


class NewPictureFeed(TasksFeed):

    def __init__(self, tasks, picture):
        TasksFeed.__init__(self, tasks)
        self.type_of_feed = global_variables.NEW_PICTURE_FEED
        self.picture = picture
        self.picture_url = self.get_picture_url()
        self.created = picture.date_uploaded

    def get_picture_url(self):
        return self.picture.task_pics.url


class NewsFeed:

    def __init__(self, type_of_feed, feed_options=None):
        self.type_of_feed_of_feed = type_of_feed
        self.feed_options = feed_options
        self.feed = self.get_feed()
        try:
            self.created = self.feed.created
        except (ObjectDoesNotExist, ValueError, AttributeError):
            self.created = None

    def get_feed(self):
        if self.type_of_feed_of_feed == global_variables.NEW_TASK_FEED:
            return TasksFeed(self.feed_options)
        elif self.type_of_feed_of_feed == global_variables.NEW_PICTURE_FEED:
            return NewPictureFeed(self.feed_options[0], self.feed_options[1])
        elif self.type_of_feed_of_feed == global_variables.NEW_PROFILE_PICTURE_FEED:
            return NewPictureFeed(self.feed_options[0], self.feed_options[1])
        return None


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






