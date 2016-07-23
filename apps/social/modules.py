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
    tasks_feed = Tasks.objects.filter(Q(is_active=True),Q(user__in=tkdge_friends))
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




