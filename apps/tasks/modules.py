from django.core.exceptions import ObjectDoesNotExist
from models import TikedgeUser

from django.db.models import Q
from datetime import timedelta, datetime
from forms import form_module
from forms.form_module import get_current_datetime
import pytz
from tzlocal import get_localzone
from global_variables_tasks import DECODE_DICTIONARY
from bs4 import BeautifulSoup
from django.contrib import messages
import global_variables_tasks
from ..social.models import Notification, LetDownMilestone, VoucheMilestone, ProfilePictures
from ..social import global_variables
from django.utils.dateparse import parse_datetime

CURRENT_URL = global_variables.CURRENT_URL

def get_user_projects(user):
    try:
        user = TikedgeUser.objects.get(user=user)
    except ObjectDoesNotExist:
        return []
    list_of_project = user.userproject_set.all().filter(is_live=True)
    t_list= []
    for proj in list_of_project:
        temp_tup = proj.name_of_project
        t_list.append(temp_tup)
    return t_list


def api_get_user_projects(user):
    try:
        user = TikedgeUser.objects.get(user=user)
    except ObjectDoesNotExist:
        return []
    list_of_project = user.userproject_set.all().filter(is_live=True, is_deleted=False)
    t_list= []
    for proj in list_of_project:
        t_list.append({'id':proj.id, 'name':proj.name_of_project})
    return t_list


def get_tikedge_user(user):
    tikedge_user = TikedgeUser.objects.get(user=user)
    return tikedge_user


def get_user_milestones(user):
    try:
        user = TikedgeUser.objects.get(user=user)
    except ObjectDoesNotExist:
        return []
    list_of_milestone = user.milestone_set.all().filter(is_active=True, is_deleted=False)
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
                                             Q(is_active=True), Q(is_deleted=False))
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


def convert_html_to_datetime(date_time, timezone='UTC'):
    if date_time:
        datetimearray = date_time.split('T')
        date = datetimearray[0]
       # print date
        time = datetimearray[1]
        new_date_time = date + ' '+time
        print new_date_time
        end_by_naive = datetime.strptime(new_date_time, '%Y-%m-%d %H:%M')
        pytz.timezone(timezone).localize(end_by_naive)
        return end_by_naive
    else:
        return False


def time_has_past(time_infos):
        if time_infos:
            if time_infos <= get_current_datetime():
                print "current date and time %s local date and time %s"% (str(get_current_datetime()),
                                                                        str(utc_to_local(get_current_datetime())))
                return True
            else:
                return False
        return True


def time_to_utc(time_to_convert):

    done_by = time_to_convert

    new_time = done_by.replace(tzinfo=get_localzone())

    the_utc = pytz.timezone('UTC')
    new_time_utc = new_time.astimezone(the_utc)
    return new_time_utc


def utc_to_local(input_time, local_timezone=""):
    if local_timezone:
        local = input_time.astimezone(local_timezone)
        return local
    else:
        return input_time


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
    status = "Learner ( Top 100 Percentile )"
    mil_all = tikedge_user.milestone_set.all().count()
    mil_success = get_completed_mil_count(user)
    milestone_count = mil_success + mil_all
    if mil_all == 0:
        return status
    ratio_percentage = float(mil_success/mil_all)*100
    if milestone_count < 5:
        return status
    else:
        if milestone_count >= 5 and milestone_count < 10:
            if ratio_percentage > 75.5:
                status = "Doer ( Top 75 Percentile )"
            return status
        if milestone_count >= 10 and milestone_count < 15:
            if ratio_percentage > 75.5:
                status = "Motivator ( Top 50 Percentile )"
            elif ratio_percentage > 60.5:
                status = "Doer ( Top 75 Percentile )"
            elif ratio_percentage > 45.5:
                status = "Learner ( Top 95 Percentile )"
            return status
        if milestone_count >= 15:
            if ratio_percentage > 75.5:
                status = "Inspires ( Top 25 Percentile )"
            elif ratio_percentage > 65.5:
                status = "Motivator ( Top 50 Percentile )"
            elif ratio_percentage > 45.5:
                status = "Doer ( Top 75 Percentile )"
            elif ratio_percentage > 25.5:
                status = "Learner ( Top 95 Percentile )"
            return status


def get_pond_status(pond_members):
    pond_count = len(pond_members)
    status = global_variables_tasks.POND_FIRST_STAGE
    mil_all = 0
    mil_success = 0
    milestone_count = mil_success + mil_all
    for tikedge_user in pond_members:
        mil_all = mil_all + tikedge_user.milestone_set.all().count()
        mil_success = mil_success + get_completed_mil_count(tikedge_user.user)
    if mil_all == 0:
        return status
    ratio_percentage = float(mil_success/mil_all)*100
    if milestone_count <= 9*pond_count:
        return status
    else:
        if milestone_count >= 10*pond_count and milestone_count < 50*pond_count:
            if ratio_percentage > 75.5:
                status = global_variables_tasks.POND_SECOND_STAGE
            return status
        if milestone_count >= 50*pond_count and milestone_count < 150*pond_count:
            if ratio_percentage > 75.5:
                status = global_variables_tasks.POND_THIRD_STAGE
            elif ratio_percentage > 60.5:
                status = global_variables_tasks.POND_SECOND_STAGE
            elif ratio_percentage > 45.5:
                status = global_variables_tasks.POND_THIRD_STAGE
            return status
        if milestone_count >= 150*pond_count:
            if ratio_percentage > 75.5:
                status = global_variables_tasks.POND_FOURTH_STAGE
            elif ratio_percentage > 65.5:
                status = global_variables_tasks.POND_THIRD_STAGE
            elif ratio_percentage > 45.5:
                status = global_variables_tasks.POND_SECOND_STAGE
            elif ratio_percentage > 25.5:
                status = global_variables_tasks.POND_FIRST_STAGE
            return status


def confirm_expired_milestone_and_project(tikedge_user):
    yesterday = form_module.get_current_datetime()
    all_milestones = tikedge_user.milestone_set.all().filter(Q(done_by__lte=yesterday), Q(is_completed=False),
                                                             Q(is_failed=False), Q(is_deleted=False))
    print "all milestone, ", all_milestones
    for each_mil in all_milestones:
        if time_has_past(each_mil.done_by):
            each_mil.is_failed = True
            each_mil.is_active = False
            each_mil.save()
            try:
                user_mil_vouch = VoucheMilestone.objects.get(tasks=each_mil)
                if user_mil_vouch.users.all():
                    let_down = LetDownMilestone(tasks=each_mil)
                    let_down.save()
                    for each_user in user_mil_vouch.users.all():
                        notification = Notification(user=each_user.user,
                                        type_of_notification=global_variables.NEW_PROJECT_LETDOWN)
                        let_down.users.add(each_user)
                        notification.save()
                    notification = Notification(user=tikedge_user.user,
                                        type_of_notification=global_variables.NEW_PROJECT_LETDOWN)
                    notification.save()
                    let_down.save()
            except ObjectDoesNotExist:
                pass
    all_project = tikedge_user.userproject_set.all().filter(Q(length_of_project__lte=yesterday), Q(is_completed=False),
                                                            ~Q(made_live=None), Q(is_failed=False), Q(is_deleted=False))
    for each_proj in all_project:
        if time_has_past(each_proj.length_of_project):
            each_proj.is_failed = True
            each_proj.is_live = False
            each_proj.save()


def get_failed_mil_count(user):
    tikedge_user = get_tikedge_user(user)
    mil_count = tikedge_user.milestone_set.all().filter(Q(is_failed=True), Q(is_deleted=False)).count()
    return mil_count


def get_completed_mil_count(user):
    tikedge_user = get_tikedge_user(user)
    mil_count = tikedge_user.milestone_set.all().filter(Q(is_completed=True), Q(is_deleted=False)).count()
    return mil_count


def get_failed_proj_count(user):
    tikedge_user = get_tikedge_user(user)
    proj_count = tikedge_user.userproject_set.all().filter(Q(is_failed=True), Q(is_deleted=False)).count()
    return proj_count


def get_completed_proj_count(user):
    tikedge_user = get_tikedge_user(user)
    proj_count = tikedge_user.userproject_set.all().filter(Q(is_completed=True), Q(is_deleted=False)).count()
    return proj_count


def get_recent_projects(user):
    tikedge_user = get_tikedge_user(user)
    all_project = tikedge_user.userproject_set.all().filter(Q(is_live=True), Q(is_deleted=False))
    return all_project


def display_error(form, request):
    for field, mes in form.errors.items():
        for error in mes:
            str_item = BeautifulSoup(mes[0], 'html.parser')
            print (str_item.get_text())
            messages.warning(request, "Field Name: %s.  Error: %s" % (form.fields[field].label, error))


def check_milestone_word_is_valid(word):
    if word:
        if (len(word) > 600) or (len(word) == 0):
            return False
        else:
            return True
    else:
        return False


def get_pic_list(pic_list):
    pass

### Api Profile Calls


def get_todays_milestones_json(user):
    """
    Return todays milestone that are due for the given user
    :param user:
    :return:
    """
    milestone_list = []
    mil_list = get_todays_milestones(user)
    for milestone in mil_list:
        milestone_list.append({
            'blurb':milestone.blurb,
            'id':milestone.id
        })
    return milestone_list


def get_recent_projects_json(user):
    project_list = []
    projects = get_recent_projects(user)
    for each_proj in projects:
        project_list.append({
            'blurb':each_proj.blurb,
            'id':each_proj.id
        })
    return project_list


def get_profile_pic_json(tikedge_user):
    try:
        has_prof_pic = ProfilePictures.objects.get(tikedge_user=tikedge_user)
    except ObjectDoesNotExist:
        has_prof_pic = None
    if has_prof_pic:
        pic_url  = CURRENT_URL + has_prof_pic.profile_pics.url
        return pic_url
    return None









