from ..tasks.models import TikedgeUser, Tasks, Milestone, UserProject
from .models import TaskPicture, ProfilePictures, Graded, Seen, Vouche, \
Notification, PictureSet, VoucheMilestone, SeenMilestone
from django.db.models import Q
from tasks_feed import TasksFeed, NewsFeed, NotificationFeed, PondFeed
from ..tasks.modules import get_query
from friendship.models import Friend
from models import User
from django.core.exceptions import ObjectDoesNotExist
import global_variables
import StringIO
from PIL import Image
from random import randint
from journal_feed import JournalFeed


def resize_image(image_field, is_profile_pic=False):
    image_file = StringIO.StringIO(image_field.read())
    image = Image.open(image_file)
    if is_profile_pic:
        image = image.resize((161, 161), Image.ANTIALIAS)
    else:
        image = image.resize((1080, 566), Image.ANTIALIAS)
    image_file = StringIO.StringIO()
    image.save(image_file, 'JPEG', quality=90)
    return image_file


def convert_list_to_profile_activities_object(type_of_feed, object_feed):
    list_of_activities = []
    if type_of_feed == global_variables.NEW_TASK_FEED:
        for item_feed in object_feed:
            new_prof_activ = NewsFeed(type_of_feed, feed_options=item_feed)
            list_of_activities.append(new_prof_activ)
    elif type_of_feed == global_variables.NEW_PICTURE_FEED:
        for item_feed in object_feed:
            print item_feed.task
            new_prof_activ = NewsFeed(type_of_feed, feed_options=[item_feed.task, item_feed])
            list_of_activities.append(new_prof_activ)
    elif type_of_feed == global_variables.NEW_PROFILE_PICTURE_FEED:
        for item_feed in object_feed:
            new_prof_activ = NewsFeed(type_of_feed, feed_options=[None, item_feed])
            list_of_activities.append(new_prof_activ)
    return list_of_activities


def get_user_activities_in_json_format(user):
    tkdge_user = TikedgeUser.objects.get(user=user)
    task_activ = Tasks.objects.filter(Q(user=tkdge_user), ~Q(start=None))
    task_activities = convert_list_to_profile_activities_object(global_variables.NEW_TASK_FEED, task_activ)
    tasks_picture_activ = TaskPicture.objects.filter(Q(tikedge_user=tkdge_user), ~Q(task=None))
    tasks_picture_activities = convert_list_to_profile_activities_object(global_variables.NEW_PICTURE_FEED,
                                                                         tasks_picture_activ)
    profile_picture_activ = ProfilePictures.objects.filter(Q(tikedge_user=tkdge_user))
    profile_picture_activities = convert_list_to_profile_activities_object(global_variables.NEW_PROFILE_PICTURE_FEED,
                                                                           profile_picture_activ)
    activities = task_activities + tasks_picture_activities \
                 + profile_picture_activities
    print activities
    activities_list = []
    if activities:
        sorted_list = sorted(activities, key=lambda feed: feed.created)
        activities_list = []

        for activ in sorted_list:
            activ_dic = {}
            if activ.type_of_feed is global_variables.NEW_PICTURE_FEED or activ.type_of_feed is global_variables.NEW_TASK_FEED:
                if activ.type_of_feed is global_variables.NEW_PICTURE_FEED:
                    activ_dic['name_of_feed'] = "Added New Picture to %s" % str(activ.feed.name_of_task)
                else:
                    activ_dic['name_of_feed'] = activ.feed.name_of_task
                activ_dic['id'] = activ.feed.id
                activ_dic['task_failed'] = activ.feed.tasks.task_failed
                activ_dic['completed'] = activ.feed.tasks.task_completed
                activ_dic['build_cred_count'] = activ.feed.build_cred_count
                activ_dic['letDown_count'] = activ.feed.letDown_count
                activ_dic['vouche_count'] = activ.feed.vouche_count
                activ_dic['seen_count'] = activ.feed.seen_count
                activ_dic['follow_count'] = activ.feed.follow_count
                activ_dic['partOfProject'] = activ.feed.tasks.part_of_project
                activ_dic['created'] = activ.created.strftime("%B %d %Y %I:%M %p")
            if activ.type_of_feed is global_variables.NEW_PROFILE_PICTURE_FEED:
                activ_dic['profile_url'] = activ.feed.picture_url
            if activ.type_of_feed is global_variables.NEW_PICTURE_FEED:
                activ_dic['picture_url'] = activ.feed.picture_url
            activities_list.append(activ_dic)
    return activities_list


def get_users_feed(user):
    list_of_feed = []
    user_friends = Friend.objects.friends(user)
    tkdge_friends = TikedgeUser.objects.filter(user__in=user_friends)
    milestone_feed = Milestone.objects.filter(Q(is_active=True),Q(user__in=tkdge_friends))
    project_feed = UserProject.objects.filter(Q(is_live=True), Q(user__in=tkdge_friends))
    picture_feed = PictureSet.objects.filter(~Q(after_picture=None), Q(tikedge_user__in=tkdge_friends))
    print "picture feed", picture_feed
    #print tasks_feed
    for each_tasks in milestone_feed:
        feed = PondFeed(each_tasks, type_of_feed=global_variables.MILESTONE)
        list_of_feed.append(feed)
    for each_tasks in project_feed:
        feed = PondFeed(each_tasks, type_of_feed=global_variables.NEW_PROJECT)
        list_of_feed.append(feed)
    for each_tasks in picture_feed:
        feed = PondFeed(each_tasks, type_of_feed=global_variables.PICTURE_SET)
        list_of_feed.append(feed)
    return list_of_feed


def get_task_feed(task):
    feed = TasksFeed(task)
    return feed


def find_people(query_word, user_owner):
    tkdge_users = []
    found_result = get_query(query_word, ['first_name', 'username', 'last_name'])
    result = User.objects.filter(found_result).filter(~Q(username=user_owner.username))
    print result
    if result:
        for user in result:
            try:
                friend_user = TikedgeUser.objects.get(user=user)
            except ObjectDoesNotExist:
                friend_user = None
            if friend_user:
                print "I was found"
                tkdge_users.append((friend_user, Friend.objects.are_friends(user_owner, user)))
    print tkdge_users
    return tkdge_users


def people_result_to_json(user_result):
    json_list = []
    for user, friend_status in user_result:
        json_dic = {}
        json_dic['username'] = user.user.username
        json_dic['first_name'] = user.user.first_name
        json_dic['last_name'] = user.user.last_name
        json_dic['are_friends'] = friend_status
        json_dic['id'] = user.id
        json_list.append(json_dic)
    return json_list


def transform_activities_feed_to_json(user):
    user_friends = Friend.objects.friends(user)
    tkdge_friends = TikedgeUser.objects.filter(user__in=user_friends)
    task_activ = Tasks.objects.filter(Q(user__in=tkdge_friends), ~Q(start=None))
    task_activities = convert_list_to_profile_activities_object(global_variables.NEW_TASK_FEED, task_activ)
    tasks_picture_activ = TaskPicture.objects.filter(Q(tikedge_user__in=tkdge_friends), ~Q(task=None))
    tasks_picture_activities = convert_list_to_profile_activities_object(global_variables.NEW_PICTURE_FEED,
                                                                         tasks_picture_activ)
    profile_picture_activ = ProfilePictures.objects.filter(Q(tikedge_user__in=tkdge_friends))
    profile_picture_activities = convert_list_to_profile_activities_object(global_variables.NEW_PROFILE_PICTURE_FEED,
                                                                           profile_picture_activ)
    activities = task_activities + tasks_picture_activities + profile_picture_activities
    print activities, " activities empty"
    activities_list = []
    if activities:
        sorted_list = sorted(activities, key=lambda feed: feed.created)
        activities_list = []

        for activ in sorted_list:
            activ_dic = {}
            if activ.type_of_feed is global_variables.NEW_PICTURE_FEED or activ.type_of_feed is global_variables.NEW_TASK_FEED:
                if activ.type_of_feed is global_variables.NEW_PICTURE_FEED:
                    activ_dic['name_of_feed'] = "Added New Picture to %s" % str(activ.feed.name_of_task)
                else:
                    activ_dic['name_of_feed'] = activ.feed.name_of_task
                activ_dic['name_of_feed'] = activ.feed.name_of_task
                activ_dic['id'] = activ.feed.id
                activ_dic['task_failed'] = activ.feed.tasks.task_failed
                activ_dic['completed'] = activ.feed.tasks.task_completed
                activ_dic['build_cred_count'] = activ.feed.build_cred_count
                activ_dic['letDown_count'] = activ.feed.letDown_count
                activ_dic['vouche_count'] = activ.feed.vouche_count
                activ_dic['seen_count'] = activ.feed.seen_count
                activ_dic['follow_count'] = activ.feed.follow_count
                activ_dic['partOfProject'] = activ.feed.tasks.part_of_project
                activ_dic['created'] = activ.created.strftime("%B %d %Y %I:%M %p")
                activ_dic['user_profile_pic_url'] = activ.feed.task_owner_profile_pic_url
                activ_dic['name_of_owner'] = activ.feed.task_owner_name
                print "%s name of user" % activ.feed.task_owner_name
            if activ.type_of_feed is global_variables.NEW_PROFILE_PICTURE_FEED:
                activ_dic['profile_url'] = activ.feed.picture_url
            if activ.type_of_feed is global_variables.NEW_PICTURE_FEED:
                activ_dic['picture_url'] = activ.feed.picture_url
            activities_list.append(activ_dic)
    return activities_list


def friend_request_to_json(friend_request, user):
    friend_request_list = []
    for each_request in friend_request:
        print friend_request, " friend request"
        rq_dic = {}
        rq_dic["username"] = each_request.from_user.username
        rq_dic["message"] = each_request.message
        rq_dic["pk"] = each_request.pk
        friend_request_list.append(rq_dic)
    return friend_request_list


def grade_user_success(user, task):
    """
    User completed task
    :param user:
    :param task:
    :return:
    """
    tikedge_user = TikedgeUser.objects.get(user=user)
    grade = Graded.objects.get(user=tikedge_user)

    try:
        vouch = Vouche.objects.get(tasks=task)
        vouch_users = vouch.users.all()
    except ObjectDoesNotExist:
        vouch_users = []
    try:
        seen = Seen.objects.get(tasks=task)
        seen_users = seen.users.filter(~Q(users__in=vouch_users))
    except ObjectDoesNotExist:
        seen_users = []
    grade.prior_consitency_count = grade.consistency_count
    grade.save()
    grade.max_consistency_count = grade.max_consistency_count + 10
    grade.consistency_count = grade.consistency_count + 10
    grade.completed_tasks = grade.completed_tasks + 1
    grade.save()
    notification = Notification(user=user, type_of_notification=global_variables.COMPLETED_TASKS,
                                tasks=task)
    notification.save()
    for user_friend in vouch_users:
        """
            vouched correctly
        """
        user_grade = Graded.objects.get(user=user_friend)
        user_grade.correct_vouch = user_grade.correct_vouch + 1
        user_grade.prior_credibility_count = user_grade.credibility_count
        user_grade.save()
        user_grade.credibility_count = user_grade.credibility_count + 10
        user_grade.max_credibility_count = user_grade.max_credibility_count + 10
        user_grade.save()
        notification = Notification(user=user_friend.user, type_of_notification=global_variables.CORRECT_VOUCH,
                                tasks=task)
        notification.save()
    for user_friend in seen_users:

        """
           missed opportunity to vouch
        """
        user_grade = Graded.objects.get(user=user_friend)
        user_grade.seen_without_vouch_success = user_grade.seen_without_vouch_success + 1
        user_grade.prior_crediblity_count = user_grade.credibility_count
        user_grade.credibility_count = user_grade.credibility_count + 7
        user_grade.max_credibility_count = user_grade.max_credibility_count + 10
        user_grade.save()
        notification = Notification(user=user_friend.user, type_of_notification=global_variables.MISSED_VOUCH_OPPURTUNITY,
                                tasks=task)
        notification.save()


def grade_user_failure(user, task):
    """
    User failed to complete tasks
    :param user:
    :param task:
    :return:
    """
    tikedge_user = TikedgeUser.objects.get(user=user)
    grade = Graded.objects.get(user=tikedge_user)

    try:
        vouch = Vouche.objects.get(tasks=task)
        vouch_users = vouch.users.all()
    except ObjectDoesNotExist:
        vouch_users = []
    try:
        seen = Seen.objects.get(tasks=task)
        seen_users = seen.users.filter(~Q(users__in=vouch_users))
    except ObjectDoesNotExist:
        seen_users = []
    grade.max_consistency_count = grade.max_consistency_count + 10
    grade.failed_tasks =+ 1
    grade.save()
    notification = Notification(user=user, type_of_notification=global_variables.FAILED_TASKS,
                                tasks=task)
    notification.save()
    for user_friend in vouch_users:
        """
            vouched incorrectly, i.e they vouched for a user that didn't finish their task
        """
        user_grade = Graded.objects.get(user=user_friend)
        user_grade.vouch_fail = user_grade.vouch_fail + 1
        user_grade.prior_credibility_count = user_grade.credibility_count
        user_grade.credibility_count = user_grade.credibility_count + 4
        user_grade.max_credibility_count = user_grade.max_credibility_count + 10
        user_grade.save()
        notification = Notification(user=user_friend.user, type_of_notification=global_variables.INCORRECT_VOUCH,
                                tasks=task)
        notification.save()
    for user_friend in seen_users:

        """
           missed opportunity to vouch
        """
        user_grade = Graded.objects.get(user=user_friend)
        user_grade.seen_without_vouch_fail = user_grade.seen_without_vouch_fail + 1
        user_grade.prior_crediblity_count = user_grade.credibility_count
        user_grade.save()
        user_grade.credibility_count = user_grade.credibility_count + 4
        user_grade.max_credibility_count = user_grade.credibility_count + 4
        user_grade.save()


def get_consistency_notification(user_obj):
    notif_list = []
    notifications = Notification.objects.filter(Q(user=user_obj, type_of_notification=global_variables.FAILED_TASKS)|
                                                   Q(user=user_obj, type_of_notification=global_variables.COMPLETED_TASKS))
    notification_feed = NotificationFeed(notifications=notifications, user=user_obj)
    unread_list = notification_feed.get_unread_notification()
    for notif in unread_list:
        new_dic = {}
        new_dic["name"] = notif.get_name()
        notif_list.append(new_dic)
    return notif_list


def get_credibility_notification(user_obj):
    notif_list = []
    notifications = Notification.objects.filter(Q(user=user_obj, type_of_notification=global_variables.MISSED_VOUCH_OPPURTUNITY)|
                                                   Q(user=user_obj, type_of_notification=global_variables.CORRECT_VOUCH) |
                                                Q(user=user_obj, type_of_notification=global_variables.INCORRECT_VOUCH))
    notification_feed = NotificationFeed(notifications=notifications, user=user_obj)
    unread_list = notification_feed.get_unread_notification()
    for notif in unread_list:
        new_dic = {}
        new_dic["name"] = notif.get_name()
        notif_list.append(new_dic)
    return notif_list


def create_grade_for_user(tikedge):
    grade_user = Graded(user=tikedge)
    grade_user.save()


def milestone_tuple(project):
    tuple_list = []
    milestones = project.milestone_set.all()
    for each_mil in milestones:
        try:
            vouch_count = VoucheMilestone.objects.get(tasks=milestones).users.count()
        except ObjectDoesNotExist:
            vouch_count = 0
        try:
            seen_count = SeenMilestone.objects.get(tasks=milestones).users.count()
        except ObjectDoesNotExist:
            seen_count = 0
        tuple_list.append((each_mil, vouch_count, seen_count))
    return tuple_list


def get_milestone_percentage(milestone):
    try:
        vouch_count = VoucheMilestone.objects.get(tasks=milestone).users.count()
    except ObjectDoesNotExist:
        vouch_count = 0
    try:
        seen_count = SeenMilestone.objects.get(tasks=milestone).users.count()
    except ObjectDoesNotExist:
        seen_count = 0
    if seen_count == 0:
        return 50
    else:
        percent = (float(vouch_count)/float(seen_count))*100
        return int(percent)


def increment_milestone_view(user_obj, milestone):
    user = TikedgeUser.objects.get(user=user_obj)
    try:
        view = SeenMilestone.objects.get(tasks=milestone)
    except ObjectDoesNotExist:
        view = SeenMilestone(tasks=milestone)
        view.save()
    if user not in view.users.all():
        view.users.add(user)
        view.save()
    print "Trying to view you!!!"


def get_journal_message(type_of_message, milestone=None, project=None):
    message = input_message(type_of_message, milestone, project)[randint(0, 2)]
    return message


def input_message(type_of_message, milestone_name, project_name):
    if type_of_message == global_variables.MILESTONE:
        LIST_OF_RANDOM_MESSAGE = [
		    'I created a new milestone named: %s, for this %s project' % (milestone_name, project_name),
		    'This %s milestone belongs to the %s project' % (milestone_name, project_name),
		    '%s milestone was created for this project: %s' % (milestone_name, project_name),
	    ]
    elif type_of_message == global_variables.BEFORE_PICTURE:
        LIST_OF_RANDOM_MESSAGE = [
            "I took a new before picture set: %s" % milestone_name,
            "Just took a new before picture for %s milestone" % milestone_name,
            "I added a new before picture to %s milestone" % milestone_name,
        ]
    elif type_of_message == global_variables.AFTER_PICTURE:
        LIST_OF_RANDOM_MESSAGE = [
            "I took a new after picture set: %s" % milestone_name,
            "Just took a new after picture for %s milestone" % milestone_name,
            "I added a new after picture to %s milestone" % milestone_name,
        ]
    else:
        LIST_OF_RANDOM_MESSAGE = [
            "Created a new project: %s." % project_name,
            "This project will get done: %s." % project_name,
            "Looking forward to this project %s" % project_name,
        ]
    return LIST_OF_RANDOM_MESSAGE


def get_user_journal_feed(tikege_user):
    journal_list = []
    journals = tikege_user.journalpost_set.all()
    for journal in journals:
        journal_feed = JournalFeed(journal)
        journal_list.append(journal_feed)
    return journal_list


