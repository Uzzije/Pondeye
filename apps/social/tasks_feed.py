#!/usr/bin/python
"""
Feed and Notification Classes for Social News Feed of Application
"""
from models import Seen, Vouche, BuildCred, Follow, LetDown, ProfilePictures
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
        self.type = global_variables.NEW_TASK_FEED
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
        if self.notif.type_of_notification == global_variables.FRIEND_REQUEST:
            name = "You have a new friend Request"
        elif self.notif.type_of_notification == global_variables.REQUEST_ACCEPTED:
            name = "Your Friend Request Has Been Accepted"
        elif self.notif.type_of_notification == global_variables.REQUEST_REJECTED:
            name = "Your Friend Request Has Been Rejected"
        elif self.notif.type_of_notification == global_variables.NEW_PICTURE_ADDED:
            task_owner_name = '%s %s' % (self.notif.picture_post.task.user.first_name,
                              self.notif.picture_post.task.user.first_name)
            name_of_task = self.notif.picture_post.task.name_of_tasks
            name = "%s Added a New Picture to %s task" % (task_owner_name, name_of_task)
        elif self.notif.type_of_notification == global_variables.PROJECT_FOLLOWING_UPDATE:
            project_owner_name = '%s %s' % (self.notif.project_update.user.first_name,
                              self.notif.project_update.user.first_name)
            project_name = self.notif.project_update.name_of_project
            name = "%s Updated %s Project" % (project_owner_name, project_name)
        else:
            name = "New Notification"
        return name


class NewPictureFeed(TasksFeed):

    def __init__(self, tasks, picture):
        TasksFeed.__init__(self, tasks)
        self.type = global_variables.NEW_PICTURE_FEED
        self.picture = picture
        self.picture_url = self.get_picture_url()
        self.created = picture.date_uploaded

    def get_picture_url(self):
        return self.picture.task_pics.url


class NewsFeed:

    def __init__(self, type_of_feed, feed_options=None):
        self.type_of_feed = type_of_feed
        self.feed_options = feed_options
        self.feed = self.get_feed()
        try:
            self.created = self.feed.created
        except (ObjectDoesNotExist, ValueError, AttributeError):
            self.created = None

    def get_feed(self):
        if self.type_of_feed == global_variables.NEW_TASK_FEED:
            return TasksFeed(self.feed_options)
        elif self.type_of_feed == global_variables.NEW_PICTURE_FEED:
            return NewPictureFeed(self.feed_options[0], self.feed_options[1])
        elif self.type_of_feed == global_variables.NEW_PROFILE_PICTURE_FEED:
            return NewPictureFeed(self.feed_options[0], self.feed_options[1])
        return None







