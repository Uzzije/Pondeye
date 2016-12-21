from django.core.exceptions import ObjectDoesNotExist
from models import TikedgeUser

from django.db.models import Q
from datetime import timedelta
from forms import form_module
from forms.form_module import get_current_datetime
import pytz
from tzlocal import get_localzone
from global_variables_tasks import DECODE_DICTIONARY
from django.utils.timezone import is_aware
from bs4 import BeautifulSoup
from django.contrib import messages


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


def get_tikedge_user(user):
    tikedge_user = TikedgeUser.objects.get(user=user)
    return tikedge_user


def get_user_milestones(user):
    try:
        user = TikedgeUser.objects.get(user=user)
    except ObjectDoesNotExist:
        return []
    list_of_milestone = user.milestone_set.all().filter(is_active=True)
    t_list= []
    for mil in list_of_milestone:
        temp_tup = ({'name':mil.name_of_milestone, 'id':mil.id})
        t_list.append(temp_tup)
    return t_list


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
                                             Q(is_active=True))
    except ObjectDoesNotExist:
        result = []
    return result


def get_todays_milestones(user):
    user = TikedgeUser.objects.get(user=user)
    tommorrow = form_module.get_current_datetime() + timedelta(hours=24)
    #print "yesterday ", yesterday,
    try:
        result = user.milestone_set.all().filter(Q(reminder__lte=tommorrow),
                                             Q(is_active=True))
    except ObjectDoesNotExist:
        result = []
    return result


def get_expired_tasks(user):
    user = TikedgeUser.objects.get(user=user)
    try:
        exp_tasks = user.milestone_set.all().filter(Q(is_active=False, current_working_on_task=True))
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


def time_has_past(time_infos):
        time_info = time_to_utc(time_infos)
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

    done_by = time_to_convert

    new_time = done_by.replace(tzinfo=get_localzone())

    the_utc = pytz.timezone('UTC')
    new_time_utc = new_time.astimezone(the_utc)
    return new_time_utc


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


def get_status(user):
    tikedge_user = get_tikedge_user(user)
    status = "The Learner"
    mil_all = tikedge_user.milestone_set.all().count()
    mil_success = get_completed_mil_count(user)
    milestone_count = mil_success + mil_all
    if mil_all == 0:
        return status
    ratio_percentage = float(mil_success/mil_all)*100
    if milestone_count < 10:
        return status
    else:
        if milestone_count >= 10 and milestone_count < 50:
            if ratio_percentage > 75.5:
                status = "The Doer"
            return status
        if milestone_count >= 50 and milestone_count < 150:
            if ratio_percentage > 75.5:
                status = "The Motivator"
            elif ratio_percentage > 60.5:
                status = "The Doer"
            elif ratio_percentage > 45.5:
                status = "The Learner"
            return status
        if milestone_count >= 150:
            if ratio_percentage > 75.5:
                status = "The Inspirer"
            elif ratio_percentage > 65.5:
                status = "The Motivator"
            elif ratio_percentage > 45.5:
                status = "The Doer"
            elif ratio_percentage > 25.5:
                status = "The Learner"
            return status


def confirm_expired_milestone_and_project(tikedge_user):
    yesterday = form_module.get_current_datetime()
    all_milestones = tikedge_user.milestone_set.all().filter(Q(done_by__lte=yesterday), Q(is_completed=False))
    for each_mil in all_milestones:
        if time_has_past(each_mil.done_by):
            each_mil.is_failed = True
            each_mil.is_active = False
            each_mil.save()

    all_project = tikedge_user.userproject_set.all().filter(Q(length_of_project__lte=yesterday), Q(is_completed=False))
    for each_proj in all_project:
        if time_has_past(each_proj.length_of_project):
            each_proj.is_failed = True
            each_proj.is_live = False
            each_proj.save()
            all_milestones = each_proj.milestone_set.all()
            for each_mil in all_milestones:
                each_mil.is_active = False
                if not each_mil.is_completed:
                    each_mil.is_failed = True
                each_mil.save()


def get_failed_mil_count(user):
    tikedge_user = get_tikedge_user(user)
    mil_count = tikedge_user.milestone_set.all().filter(Q(is_failed=True)).count()
    return mil_count


def get_completed_mil_count(user):
    tikedge_user = get_tikedge_user(user)
    mil_count = tikedge_user.milestone_set.all().filter(Q(is_completed=True)).count()
    return mil_count


def get_failed_proj_count(user):
    tikedge_user = get_tikedge_user(user)
    proj_count = tikedge_user.userproject_set.all().filter(Q(is_failed=True)).count()
    return proj_count


def get_completed_proj_count(user):
    tikedge_user = get_tikedge_user(user)
    proj_count = tikedge_user.userproject_set.all().filter(Q(is_completed=True)).count()
    return proj_count


def get_recent_projects(user):
    tikedge_user = get_tikedge_user(user)
    all_project = tikedge_user.userproject_set.all().filter(Q(is_live=True))
    return all_project

def display_error(form, request):
	for field, mes in form.errors.items():
		str_item = BeautifulSoup(mes[0], 'html.parser')
		print (str_item.get_text())
		messages.warning(request, "%s" % mes[0])

