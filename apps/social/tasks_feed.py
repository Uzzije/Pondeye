#!/usr/bin/python
"""
Feed and Notification Classes for Social News Feed of Application
"""
from models import Seen, Vouche, BuildCred, Follow, LetDown
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
        self.name_of_task = tasks.name_of_tasks, " from " + self.get_start_time()+ " to " + self.get_end_time()
        self.id = tasks.id

    def seens(self):
        try:
            seensd = Seen.objects.get(tasks=self.tasks)
            count = seensd.users.count()
        except ObjectDoesNotExist:
            count = 0
        return count

    def get_start_time(self):
        return self.tasks.start.strftime("%I:%M %p")

    def get_end_time(self):
        return self.tasks.end.strftime("%I:%M %p")

    def vouche(self):
        try:
            vouched = Vouche.objects.get(tasks=self.tasks)
            count = vouched.users.count()
        except ObjectDoesNotExist:
            count = 0
        return count


    def build_cred(self):
        try:
            buildCred = BuildCred.objects.get(tasks=self.tasks)
            count = buildCred.users.count()
        except ObjectDoesNotExist:
            count = 0
        return count

    def follow(self):
        count = 0
        if self.tasks.part_of_project:
            try:
                follows = Follow.objects.get(tasks=self.tasks.project)
                count = follows.users.count()
            except ObjectDoesNotExist:
                pass
        return count

    def letDown(self):
        try:
            let_down = LetDown.objects.get(tasks=self.tasks)
            count = let_down.users.count()
        except ObjectDoesNotExist:
            count = 0
        return count


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
            name = "Your Friend Request Has Been rejected"
        else:
            name = "New Notification"
        return name








