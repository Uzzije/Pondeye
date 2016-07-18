#!/usr/bin/python
from models import Seen, Vouche, BuildCred, Follow, LetDown, Notification
from friendship.models import FriendshipRequest
from django.db.models import Q
import global_variables


class TasksFeed:

    def __init__(self, tasks):
        self.tasks = tasks
        self.seen_count = self.seens()
        self.vouche_count = self.vouche()
        self.build_cred_count = self.build_cred()
        self.follow_count = self.follow()
        self.letDown_count = self.letDown()

    def seens(self):
        seensd = Seen.objects.get(tasks=self.tasks)
        count = seensd.users.count()
        return count
    #seen_count = seens()

    def vouche(self):
        vouched = Vouche.objects.get(tasks=self.tasks)
        count = vouched.users.count()
        return count
    #vouche_count = vouche()

    def build_cred(self):
        buildCred = BuildCred.objects.get(tasks=self.tasks)
        count = buildCred.users.count()
        return count
    #build_cred_count = build_cred()

    def follow(self):
        follows = Follow.objects.get(tasks=self.tasks)
        count = follows.users.count()
        return count
    #follow_count = follow()

    def letDown(self):
        letDown = LetDown.objects.get(tasks=self.tasks)
        count = letDown.users.count()
        return count
    #letDown_count = letDown()


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
            name = "You have a new friend Request",
        elif self.notif.type_of_notification == global_variables.REQUEST_ACCEPTED:
            name = "Your Friend Request Has Been Accepted"
        elif self.notif.type_of_notification == global_variables.REQUEST_REJECTED:
            name = "Your Friend Request Has Been rejected"
        else:
            name = "New Notification"
        return name
    #name = get_name()








