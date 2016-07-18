from ..tasks.models import TikedgeUser, Tasks
from django.db.models import Q
from tasks_feed import TasksFeed
from ..tasks.modules import get_query
from friendship.models import Friend


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


def find_people(query_word, user_owner):
    tkdge_users = []
    result = get_query(query_word, ['first_name', 'username', 'last_name'])
    for user in result:
        friend_user = TikedgeUser.objects.get(user=user)
        tkdge_users.append((friend_user, Friend.objects.are_friends(user_owner, user)))
    return tkdge_users




