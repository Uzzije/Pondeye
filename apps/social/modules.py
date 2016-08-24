from ..tasks.models import TikedgeUser, Tasks
from django.db.models import Q
from tasks_feed import TasksFeed
from ..tasks.modules import get_query
from friendship.models import Friend
from models import User
from django.core.exceptions import ObjectDoesNotExist


def get_user_activities(user):
    tkdge_user = TikedgeUser.objects.get(user=user)
    activities = Tasks.objects.filter(Q(user=tkdge_user), Q(is_active=True)).order_by('-start')
    return activities


def get_users_feed(user):
    list_of_feed = []
    user_friends = Friend.objects.friends(user)
    tkdge_friends = TikedgeUser.objects.filter(user__in=user_friends)
    print user_friends, " friends"
    tasks_feed = Tasks.objects.filter(Q(is_active=True),Q(user__in=tkdge_friends))
    print tasks_feed
    for each_tasks in tasks_feed:
        feed = TasksFeed(each_tasks)
        list_of_feed.append(feed)
    return list_of_feed


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


def transform_activities_feed_to_json(activities):
    activities_list = []
    for activ in activities:
        activ_dic = {}
        activ_dic['name_of_feed'] = activ.name_of_task
        activ_dic['id'] = activ.id
        activ_dic['task_failed'] = activ.tasks.task_failed
        activ_dic['completed'] = activ.tasks.task_completed
        activ_dic['build_cred_count'] = activ.build_cred_count
        activ_dic['letDown_count'] = activ.letDown_count
        activ_dic['vouche_count'] = activ.vouche_count
        activ_dic['seen_count'] = activ.seen_count
        activ_dic['follow_count'] = activ.follow_count
        activ_dic['partOfProject'] = activ.tasks.part_of_project
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


