#!/usr/bin/python
"""
Feed and Notification Classes for Social News Feed of Application
"""
from models import ProfilePictures,\
    BuildCredMilestone, SeenMilestone, SeenPictureSet, SeenProject, VoucheMilestone, Follow
from friendship.models import FriendshipRequest
from django.db.models import Q
import global_variables
from django.core.exceptions import ObjectDoesNotExist


class PondFeed:

    def __init__(self, tasks, type_of_feed):
        self.tasks = tasks
        self.type_of_feed = type_of_feed
        self.seen_count = self.seens()
        self.vouche_count = self.vouche()
        self.follow_count = self.follow()
        self.task_owner_name = self.get_name()
        self.is_milestone_feed = self.is_milestone_feed()
        self.is_picture_feed = self.is_picture_feed()
        self.is_project_feed = self.is_project_feed()
        self.message = self.message()
        self.before_url = self.get_before_url()
        self.after_url = self.get_after_url()
        self.feed_id = self.tasks.id
        self.created = self.get_date_created()
        self.profile_url = self.task_owner_profile_pic_url()
        self.feed_user = self.get_user_tikedge().user

    def get_user_tikedge(self):
        if self.type_of_feed is global_variables.PICTURE_SET:
            return self.tasks.tikedge_user
        else:
            return self.tasks.user

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
            message = "I created a new milestone: %s . This is for project: %s." % \
                      (self.tasks.name_of_milestone, self.tasks.project.blurb)
            return message
        elif self.type_of_feed is global_variables.PICTURE_SET:
            message = "I entered a journal entry for this milestone: %s." % self.tasks.milestone.blurb
            return message
        elif self.type_of_feed is global_variables.NEW_PROJECT:
            message = "Hey, I am starting a new project. Project Name: %s" % self.tasks.blurb
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
            profile_picture = ProfilePictures.objects.get(tikedge_user=self.get_user_tikedge())
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

    def highight_new_notification(self):
        unread_notify = self.notification.filter(Q(read=False)).order_by('created')
        pond_request = False
        pond_request_accepted = False
        new_ponder = False
        interested = False
        let_down = False
        milestone_vouch = False
        for each_notif in unread_notify:
            if each_notif.type_of_notification == global_variables.POND_REQUEST:
                pond_request = True
            if each_notif.type_of_notification == global_variables.POND_REQUEST_ACCEPTED:
                pond_request_accepted = True
            if each_notif.type_of_notification == global_variables.NEW_PONDERS:
                new_ponder = True
            if each_notif.type_of_notification == global_variables.NEW_PROJECT_INTERESTED:
                interested = True
            if each_notif.type_of_notification == global_variables.NEW_PROJECT_LETDOWN:
                let_down = True
            if each_notif.type_of_notification == global_variables.NEW_PROJECT_MILESTONE:
                milestone_vouch = True
        notification_dic = {
            "pond_request":pond_request,
            "pond_request_accepted":pond_request_accepted,
            "new_ponder":new_ponder,
            "interested":interested,
            "let_down":let_down,
            "milestone_vouch":milestone_vouch
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






