from ..tasks.models import TikedgeUser, Tasks
from .models import TaskPicture, ProfilePictures
from django.db.models import Q
from tasks_feed import TasksFeed, NewsFeed
from ..tasks.modules import get_query
from friendship.models import Friend
from models import User
from django.core.exceptions import ObjectDoesNotExist
import global_variables


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
    task_activ = Tasks.objects.filter(Q(user=tkdge_user), Q(is_active=True))
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
    tasks_feed = Tasks.objects.filter(Q(is_active=True),Q(user__in=tkdge_friends))
    print tasks_feed
    for each_tasks in tasks_feed:
        feed = TasksFeed(each_tasks)
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
    task_activ = Tasks.objects.filter(Q(user__in=tkdge_friends), Q(is_active=True))
    task_activities = convert_list_to_profile_activities_object(global_variables.NEW_TASK_FEED, task_activ)
    tasks_picture_activ = TaskPicture.objects.filter(Q(tikedge_user__in=tkdge_friends))
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

