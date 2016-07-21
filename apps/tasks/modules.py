from django.core.exceptions import ObjectDoesNotExist
from models import TikedgeUser, Tasks
import re
from django.db.models import Q
from datetime import timedelta
from forms import form_module
from django.db.models import Min
import time


def get_user_projects(user):
    try:
        user = TikedgeUser.objects.get(user=user)
    except ObjectDoesNotExist:
        return []
    list_of_project = user.userproject_set.all()
    t_list= []
    for proj in list_of_project:
        temp_tup = (proj.name_of_project)
        t_list.append(temp_tup)
    return t_list


def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:

        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']

    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]


def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.

    '''
    query = None # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        print term
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query


def tasks_search(query, user):
    tkedge = TikedgeUser.objects.get(user=user)
    query_result = get_query(query, ['name_of_tasks'])
    found_queries = Tasks.objects.filter(query_result).filter(Q(user=tkedge))
    return found_queries


def get_current_todo_list(user):
    user = TikedgeUser.objects.get(user=user)
    print user
    try:
        result = user.tasks_set.all().filter(Q(start__lte=form_module.get_current_datetime()),
                                                  Q(task_completed=False), Q(task_failed=False), Q(is_active=True))
        if result:
            if len(result) == 1:
                for res in result:
                    return res
            else:
                tasks = None
                for res in result:
                    if tasks and tasks.start.time() > res.start.time():
                        tasks = res
                    if tasks is None:
                        tasks = res
                return tasks
    except ObjectDoesNotExist:
        result = None
    return result


def get_todays_todo_list(user):
    user = TikedgeUser.objects.get(user=user)
    yesterday = form_module.get_current_datetime() - timedelta(days=1)
    try:
        result = user.tasks_set.all().filter(Q(start__lte=form_module.get_current_datetime()),
                                             Q(start__gte=yesterday), Q(is_active=True))
    except ObjectDoesNotExist:
        result = []
    return result


def is_time_conflict(user, start_time, end_time):
    if end_time:
        new_end = start_time + timedelta(minutes=int(end_time))
    else:
        new_end = start_time + timedelta(minutes=60)
    yesterday = form_module.get_current_datetime() - timedelta(days=1)
    user = TikedgeUser.objects.get(user=user)
    todo_todo = user.tasks_set.all().filter(Q(start__lte=start_time), Q(start__gte=yesterday),Q(is_active=True))
    for task in todo_todo:
        if task.start.time() <= start_time.time() and task.end.time() >= start_time.time() or \
                                task.start.time() <= new_end.time() and task.end.time() >= new_end.time():
            return True
    return False
