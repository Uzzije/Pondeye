from ..tasks.models import TikedgeUser
from .models import ProfilePictures, Graded, \
    Notification, VoucheMilestone, SeenMilestone, SeenProject, Follow, LetDownMilestone
from django.db.models import Q
from tasks_feed import NotificationFeed
from friendship.models import Friend
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
            vouch_count = VoucheMilestone.objects.get(tasks=each_mil).users.count()
        except ObjectDoesNotExist:
            vouch_count = 0
        try:
            seen_count = SeenMilestone.objects.get(tasks=each_mil).users.count()
        except ObjectDoesNotExist:
            seen_count = 0
        tuple_list.append((each_mil, vouch_count, seen_count))
    return tuple_list


def get_interest_notification(all_project):
    interest_feed = []
    for project in all_project:
        seen_project = Follow.objects.get(tasks=project)
        for each_follow in seen_project.users.all():
            interest_feed.append({
                'username':each_follow.user.username,
                'first_name':each_follow.user.first_name,
                'last_name':each_follow.user.last_name,
                'slug':project.slug,
                'blurb':project.blurb,
                'created':project.created
            })
    sorted_feed = sorted(interest_feed, key=lambda x: x['created'], reverse=True)
    return sorted_feed


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


def increment_project_view(user_obj, project):
    user = TikedgeUser.objects.get(user=user_obj)
    try:
        view = SeenProject.objects.get(tasks=project)
    except ObjectDoesNotExist:
        view = SeenProject(tasks=project)
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


def get_notifications(user, tikedge_user):
    notifications = user.notification_set.all()
    nofication_feed = NotificationFeed(user, notifications)
    return nofication_feed.get_unread_notification()


def get_pond(user):
    dict_list_of_pond = []
    friends = Friend.objects.friends(user)
    for each_friend in friends:
        tikedge_user = TikedgeUser.objects.get(user=each_friend)
        try:
            picture = ProfilePictures.objects.get(tikedge_user=tikedge_user)
            picture_url = picture.profile_pics.url
        except ObjectDoesNotExist:
            picture_url = None
        friend = Friend.objects.get(to_user=each_friend, from_user=user)
        dict_list_of_pond.append({
            'profile_pics_url':picture_url,
            'username':each_friend.username,
            'first_name':each_friend.first_name,
            'last_name':each_friend.last_name,
            'created':friend.created
        })
    sorted_pond = sorted(dict_list_of_pond, key=lambda pond: pond['created'])
    return sorted_pond


def get_let_down_notifications(user):
    tikedge_user = TikedgeUser.objects.get(user=user)
    milestones = tikedge_user.milestone_set.all()
    let_down_list = []
    for each_mil in milestones:
        try:
            let_down = LetDownMilestone.objects.get(tasks=each_mil)
            count = let_down.users.count()
            let_down_list.append({
            'name_of_blurb':each_mil.blurb,
            'slug':each_mil.slug,
            'count':count
            })
        except ObjectDoesNotExist:
            pass
    return let_down_list


def get_milestone_vouch_notifications(user):
    tikedge_user = TikedgeUser.objects.get(user=user)
    milestones = tikedge_user.milestone_set.all()
    mil_vouch_list = []
    for each_mil in milestones:
        print " each mil", each_mil
        try:
            mil_vouch = VoucheMilestone.objects.get(tasks=each_mil)
            count = mil_vouch.users.count()
            mil_vouch_list.append({
                'blurb':each_mil.blurb,
                'slug':each_mil.slug,
                'count':count
            })
        except ObjectDoesNotExist:
            pass
    return mil_vouch_list

