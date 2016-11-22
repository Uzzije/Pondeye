from django.core.exceptions import ObjectDoesNotExist
from models import TikedgeUser, Tasks
import re
from django.db.models import Q
from datetime import timedelta, datetime
from forms import form_module
from django.db.models import Min
from forms.form_module import get_current_datetime
from tzlocal import get_localzone
from django.utils import timezone
import time
import pytz
from dateutil.tz import *
from dateutil.tz import tzlocal
from tzlocal import get_localzone

DECODE_DICTIONARY = {'a':'c', 'b':'z', 'c':'g', 'd':'h', 'e':'w', 'f':'x', 'g':'a', 'h':'b', 'i':'d', 'j':'e', 'k':'f', 'l':'i', 'm':'j', 'n':'k', 'o':'l',
                     'p':'m', 'q':'o', 'r':'p', 's':'q', 't':'r',
                    'u':'s', 'v':'t', 'w':'y', 'x':'v', 'y':'u', 'z':'n'}


def get_user_projects(user):
    try:
        user = TikedgeUser.objects.get(user=user)
    except ObjectDoesNotExist:
        return []
    list_of_project = user.userproject_set.all().filter(is_live=True)
    t_list= []
    for proj in list_of_project:
        temp_tup = (proj.name_of_project)
        t_list.append(temp_tup)
    return t_list


def get_user_milestones(user):
    try:
        user = TikedgeUser.objects.get(user=user)
    except ObjectDoesNotExist:
        return []
    list_of_milestone = user.milestone_set.all().filter(is_active=True)
    t_list= []
    for mil in list_of_milestone:
        temp_tup = (mil.name_of_milestone)
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


def get_current_todo_list_json_form(user):
    todo_item = get_current_todo_list(user)
    if not todo_item:
        return None
    todo_json_form = {'name_of_task':todo_item.name_of_tasks, 'start_time':todo_item.start.strftime("%B %d %Y %I:%M %p"),
                      'end_time':todo_item.end.strftime("%B %d %Y %I:%M %p")}
    return todo_json_form


def stringify_task(task):
    task_string = '%s starts at %s, ends at %s' % (task.name_of_tasks, task.start.strftime("%B %d %Y %I:%M %p"),
           task.end.strftime("%B %d %Y %I:%M %p"))
    return task_string


def get_todays_todo_list_json(user):
    todays_list_array = []
    todays_list = get_todays_todo_list(user)
    print todays_list
    if not todays_list:
        return []
    for item in todays_list:
        list_to_json_form = {}
        list_to_json_form['name_of_task'] = item.name_of_tasks
        list_to_json_form['id'] = item.id
        list_to_json_form['start'] = item.start.strftime("%I:%M %p")
        list_to_json_form['end'] = item.end.strftime("%I:%M %p")
        todays_list_array.append(list_to_json_form)
    print todays_list
    return todays_list_array


def get_todays_todo_list(user):
    user = TikedgeUser.objects.get(user=user)
    yesterday = form_module.get_current_datetime() - timedelta(days=1)
    print yesterday
    try:
        result = user.tasks_set.all().filter(Q(start__lte=form_module.get_current_datetime()),
                                             Q(start__gte=yesterday), Q(is_active=True))
    except ObjectDoesNotExist:
        result = []
    return result


def get_expired_tasks(user):
    user = TikedgeUser.objects.get(user=user)
    try:
        exp_tasks = user.tasks_set.all().filter(Q(is_active=False, current_working_on_task=True))
        print "expired"
    except ObjectDoesNotExist:
        exp_tasks = []
    return exp_tasks


def get_expired_tasks_json(user):
    expired_tasks_list = []
    expired_tasks = get_expired_tasks(user)
    if expired_tasks:
        for each_task in expired_tasks:
            temp_dic = {}
            temp_dic["name_of_task"] = each_task.name_of_tasks
            temp_dic["start"] = each_task.start.strftime("%B %d %Y %I:%M %p")
            temp_dic["end"] = each_task.end.strftime("%B %d %Y %I:%M %p")
            temp_dic["pk"] = each_task.pk
            expired_tasks_list.append(temp_dic)
    return expired_tasks_list


def is_time_conflict(user, start_time, end_time):
    if end_time:
        new_end = start_time + timedelta(minutes=int(end_time))
    else:
        new_end = start_time + timedelta(minutes=60)
    print new_end
    yesterday = form_module.get_current_datetime() - timedelta(days=1)
    user = TikedgeUser.objects.get(user=user)
    todo_todo = user.tasks_set.all().filter(Q(start__lte=start_time), Q(start__gte=yesterday),Q(is_active=True))
    print todo_todo
    for task in todo_todo:
        if task.start.time() <= start_time.time() and task.end.time() >= start_time.time() or \
                                task.start.time() <= new_end.time() and task.end.time() >= new_end.time():
            return True
    return False


def is_time_conflict_mil(user, start_time, new_end, project):
    yesterday = form_module.get_current_datetime() - timedelta(days=1)
    user = TikedgeUser.objects.get(user=user)
    todo_todo = user.milestone_set.all().filter(Q(reminder__lte=start_time), Q(reminder__gte=yesterday),
                                                Q(is_active=True), Q(project=project))
    print "this is yesterday ", yesterday
    for task in todo_todo:
        if task.reminder.time() <= start_time.time() and task.done_by.time() >= start_time.time() or \
                                task.reminder.time() <= new_end.time() and task.done_by.time() >= new_end.time():
            return True
    return False


def decode_password(password):
    decoded_string =''
    for each_word in password:
        decode_letter = DECODE_DICTIONARY[each_word]
        decoded_string = decoded_string.join(decode_letter)
    return decoded_string


def convert_html_to_datetime(date_time):
    datetimearray = date_time.split('T')
    date = datetimearray[0]
   # print date
    time = datetimearray[1]
    new_date_time = date + ' '+time
    print new_date_time
    return new_date_time


def time_has_past(time_info):
        if time_info:
            if time_info.time() < get_current_datetime().time():
                if time_info.date() > get_current_datetime().date():
                    return False
                msg = "Hey, your work is not history yet"
            else:
                if time_info.date() >= get_current_datetime().date():
                    return False
                msg = "Hey, your work is not history yet"
            return msg
        return False


def time_to_utc(time_to_convert):
    loc_ndt = time_to_convert.replace(tzinfo=None)
    loc_dt = loc_ndt.replace(tzinfo=get_localzone())
    local = get_localzone().localize(loc_ndt).astimezone(pytz.utc)
    return local


def utc_to_local(input_time):
    local_tz = get_localzone()
    local = input_time.astimezone(local_tz)
    return local


def get_task_picture_urls(task):
    pic_urls = []
    pictures = task.taskpicture_set.all()
    for e_pic in pictures:
        pic_urls.append(e_pic.task_pics.url)
    return pic_urls


def json_all_pending_tasks(tasks):
    expired_tasks = []
    if tasks:
        for each_task in tasks:
            temp_dic = {}
            temp_dic["name_of_task"] = each_task.name_of_tasks
            temp_dic["id"] = each_task.id
            expired_tasks.append(temp_dic)
    return expired_tasks
