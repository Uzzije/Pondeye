from django.core.exceptions import ObjectDoesNotExist
from models import TikedgeUser, Milestone, UserProject, PasswordReset

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
from ..social.models import Notification, ProgressPictureSet, ProfilePictures, \
    PondSpecificProject, Pond, ProjectPicture, VoucheProject, LetDownProject, ProgressImpressedCount, Follow
from ..social import global_variables
import random, string
from django.utils import timezone as django_timezone
from random import randint

CURRENT_URL = global_variables.CURRENT_URL


def add_file_to_project_pic(picture_file, project):
    new_pic = ProjectPicture(image_name=picture_file.name, picture=picture_file, project=project)
    new_pic.save()


def get_project_pic_info(each_proj):
    try:
       project_picture = ProjectPicture.objects.get(project=each_proj, is_deleted=False)
       proj_pic_id = project_picture.id
       project_pic_url = CURRENT_URL + project_picture.picture.url
       has_pic = True
    except:
       proj_pic_id = None
       project_pic_url = None
       has_pic = False
    project_picture = {'pic_id':proj_pic_id, 'url':project_pic_url, 'has_pic':has_pic}
    return project_picture


def delete_project_picture(pic_id):
    picture = ProjectPicture.objects.get(id=int(pic_id))
    picture.is_deleted = False
    picture.save()


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


def get_todays_milestones(user, current_projects):
    user = TikedgeUser.objects.get(user=user)
    tommorrow = form_module.get_current_datetime() + timedelta(hours=24)
    #print "yesterday ", yesterday,
    try:
        result = user.milestone_set.all().filter(Q(reminder__lte=tommorrow),
                                             Q(is_active=True), Q(is_deleted=False), Q(project__in=current_projects))
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
        fmt = '%Y-%m-%d %H:%M:%S %Z%z'
        end_by_naive = datetime.strptime(new_date_time, '%Y-%m-%d %H:%M')
        pytz.timezone(timezone).localize(end_by_naive)
        print "end_by_naive ", django_timezone.is_aware(end_by_naive)
        made_aware = django_timezone.make_aware(end_by_naive, timezone=pytz.timezone(timezone))
        print "made aware ", made_aware.strftime(fmt), django_timezone.is_aware(made_aware)
        return made_aware
    else:
        return False


def time_has_past(time_infos, timezone=""):
        if time_infos:
            if django_timezone.localtime(time_infos) < get_current_datetime():
                print "current date and time %s local date and time %s"% (str(get_current_datetime()),
                                                                        str(time_infos))
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
    """
    All timezone should be converted to to utc timezone
    :param input_time:
    :param local_timezone:
    :return:
    """
    if local_timezone:
        try:
            local = pytz.timezone(local_timezone).normalize(input_time.astimezone(pytz.timezone(local_timezone)))
            return local
        except ValueError:
            new_time = input_time.replace(tzinfo=get_localzone())
            local = pytz.timezone(local_timezone).normalize(new_time.astimezone(pytz.timezone(local_timezone)))
            return local
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
    status = 0
    proj_all = tikedge_user.userproject_set.all().count()
    proj_success = get_completed_proj_count(user)
    project_count = proj_success + proj_all
    if proj_all == 0:
        return status
    ratio_percentage = float(proj_success/proj_all)*100
    if project_count < 5:
        return status
    else:
        if project_count >= 5 and project_count < 10:
            if ratio_percentage > 75.5:
                status = 20
            return status
        if project_count >= 10 and project_count < 15:
            if ratio_percentage > 75.5:
                status = 30
            elif ratio_percentage > 60.5:
                status = 20
            elif ratio_percentage > 45.5:
                status = 10
            return status
        if project_count >= 15:
            if ratio_percentage > 75.5:
                status = 35
            elif ratio_percentage > 65.5:
                status = 30
            elif ratio_percentage > 45.5:
                status = 20
            elif ratio_percentage > 25.5:
                status = 10
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
        if milestone_count >= 3*pond_count and milestone_count < 10*pond_count:
            if ratio_percentage > 75.5:
                status = global_variables_tasks.POND_SECOND_STAGE
            return status
        if milestone_count >= 10*pond_count and milestone_count < 15*pond_count:
            if ratio_percentage > 75.5:
                status = global_variables_tasks.POND_THIRD_STAGE
            elif ratio_percentage > 60.5:
                status = global_variables_tasks.POND_SECOND_STAGE
            elif ratio_percentage > 45.5:
                status = global_variables_tasks.POND_THIRD_STAGE
            return status
        if milestone_count >= 15*pond_count:
            if ratio_percentage > 75.5:
                status = global_variables_tasks.POND_FOURTH_STAGE
            elif ratio_percentage > 65.5:
                status = global_variables_tasks.POND_THIRD_STAGE
            elif ratio_percentage > 45.5:
                status = global_variables_tasks.POND_SECOND_STAGE
            elif ratio_percentage > 25.5:
                status = global_variables_tasks.POND_FIRST_STAGE
            return status


def confirm_expired_milestone_and_project():
    yesterday = form_module.get_current_datetime()
    '''
    all_milestones = Milestone.objects.all().filter(Q(done_by__lte=yesterday), Q(is_completed=False),
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
                    try:
                        LetDownMilestone.objects.get(tasks=each_mil)
                    except ObjectDoesNotExist:
                        let_down = LetDownMilestone(tasks=each_mil)
                        let_down.save()
                        for each_user in user_mil_vouch.users.all():
                            notification = Notification(user=each_user.user,
                                            type_of_notification=global_variables.NEW_PROJECT_LETDOWN)
                            let_down.users.add(each_user)
                            notification.save()
                        let_down.save()
            except ObjectDoesNotExist:
                pass
    '''
    all_project = UserProject.objects.all().filter(Q(length_of_project__lte=yesterday), Q(is_completed=False),
                                                            ~Q(made_live=None), Q(is_failed=False), Q(is_deleted=False))
    for each_proj in all_project:
        if time_has_past(each_proj.length_of_project):
            each_proj.is_failed = True
            each_proj.is_live = False
            each_proj.save()
            try:
                user_proj_vouch = VoucheProject.objects.get(tasks=each_proj)
                if user_proj_vouch.get_count() > 0:
                    try:
                        LetDownProject.objects.get(tasks=each_proj)
                    except ObjectDoesNotExist:
                        let_down = LetDownProject(tasks=each_proj)
                        let_down.save()
                        let_down_mess = "%s %s let you down by failing to complete this goal: %s"\
                                        % (each_proj.user.user.first_name, each_proj.user.user.first_name, each_proj.name_of_project )
                        for each_user in user_proj_vouch.users.all():
                            notification = Notification(user=each_user.user, name_of_notification=let_down_mess,
                                            type_of_notification=global_variables.NEW_PROJECT_LETDOWN)
                            let_down.users.add(each_user)
                            notification.save()
                        let_down.save()
            except ObjectDoesNotExist:
                pass


def get_failed_mil_count(user):
    tikedge_user = get_tikedge_user(user)
    mil_count = tikedge_user.milestone_set.all().filter(Q(is_failed=True), Q(is_deleted=False)).count()
    return mil_count


def get_completed_mil_count(user):
    tikedge_user = get_tikedge_user(user)
    mil_count = tikedge_user.milestone_set.all().filter(Q(is_completed=True), Q(is_deleted=False)).count()
    return mil_count


def get_failed_proj_count(user):
    """
    Grab list of failed milestones by users
    :param user:
    :return:
    """
    tikedge_user = get_tikedge_user(user)
    proj_count = tikedge_user.userproject_set.all().filter(Q(is_failed=True), Q(is_deleted=False)).count()
    return proj_count


def get_completed_proj_count(user):
    """
    Grab list of completed goal by users
    :param user:
    :return:
    """
    tikedge_user = get_tikedge_user(user)
    proj_count = tikedge_user.userproject_set.all().filter(Q(is_completed=True), Q(is_deleted=False)).count()
    return proj_count


def user_stats(user):
    """
    Grab user stats to show in profile page
    :param user: user's object
    :return: a dictionay of such items
    """
    tikedge_user = get_tikedge_user(user)
    goal_success_count = get_completed_proj_count(user)
    goal_failed_count = get_failed_proj_count(user)
    total = goal_success_count + goal_failed_count
    consistency_percentage = float((goal_success_count/total)*100)
    consistency_grade = get_letter_grade(consistency_percentage)
    total_times_impressed = user_total_impress_count(tikedge_user)
    total_goal_followers = user_total_goal_followers(tikedge_user)
    correct_vouch_percentage = correct_vouching_percentage(tikedge_user)
    correct_vouch_grade = get_letter_grade(correct_vouch_percentage)
    rank = get_user_consistency_rank(user, consistency_percentage)
    stats_dic = {
        'goal_success_count':goal_success_count,
        'goal_failed_count':goal_failed_count,
        'total':total,
        'consistency_percentage':consistency_percentage,
        'consistency_grade':consistency_grade,
        'total_times_impressed': total_times_impressed,
        'total_goal_followers': total_goal_followers,
        'correct_vouch_percentage':correct_vouch_percentage,
        'correct_vouch_grade':correct_vouch_grade,
        'rank':rank
    }

    return stats_dic


def get_user_consistency_rank(user, consistency_percentage):
    points = get_status(user)
    rank = consistency_percentage + points
    return rank


def get_letter_grade(percentage):
    """
    Convert rounded percentage into lettter grade
    :param percentage:
    :return:
    """
    if percentage < 60.0:
        return 'F'
    if percentage < 70.0:
        return 'D'
    if percentage < 80.0:
        return 'C'
    if percentage < 90.0:
        return 'B'
    return 'A'


def pond_leader_board_rank(pond):
    """
    Returns the a leaderboard list of pond members based on rank
    :param pond:
    :return:
    """
    leader_list = []
    for each_member in pond.pond_members.all():
        stats = user_stats(each_member.user)
        leader_list.append({
            'first_name': each_member.user.first_name,
            'last_name': each_member.user.last_name,
            'profile_pic':get_profile_pic_json(each_member),
            'percentage': stats['consistency_percentage'],
            'grade': stats['consistency_grade'],
            'rank': stats['rank']
        })
    sorted_leader_list = sorted(leader_list, key=lambda x: x['rank'], reverse=True)
    return sorted_leader_list


def user_total_impress_count(tikedge_user):
    """
    Get user total count of people impressed by their progress
    :param tikedge_user: tikedge_user Object
    :return: Count of all impressed user objects
    """

    impress_count = 0
    projects = tikedge_user.userproject_set.all().filter(is_deleted=False)
    for each_proj in projects:
        progress_set = ProgressPictureSet.objects.get(project=each_proj)
        for each_progress  in progress_set.list_of_progress_pictures.all(is_deleted=False):
            impress_count += ProgressImpressedCount(tasks=each_progress).get_count()
    return impress_count


def user_total_goal_followers(tikedge_user):
    """
    Get user total count of everybody following user's goals.
    :param tikedge_user: tikedge_user Object
    :return: Count of all impressed user objects
    """

    follow_count = 0
    followers_list = []
    projects = tikedge_user.userproject_set.all().filter(is_deleted=False)
    for each_proj in projects:
        followers = Follow.objects.get(tasks=each_proj)
        for each_followers  in followers.users.all():
            if each_followers not in followers_list:
                follow_count += 0
                followers_list.append(each_followers)
    return follow_count


def correct_vouching_percentage(tikedge_user):

    project_vouches = VoucheProject.objects.filter(user=tikedge_user)
    let_down_vouches = LetDownProject.objects.filter(user=tikedge_user)
    project_vouches_count = project_vouches.count()
    let_down_count = let_down_vouches.count()
    total_count = project_vouches_count + let_down_count
    correct_vouch = float((project_vouches_count/total_count)*100)
    return correct_vouch



def get_recent_projects(user, requesting_user, is_live=True):
    tikedge_user = get_tikedge_user(user)
    request_user_ponds = Pond.objects.filter(pond_members=requesting_user)
    all_project = tikedge_user.userproject_set.all().filter(Q(is_live=is_live), Q(is_deleted=False)).distinct()
    private_project = all_project.filter(is_public=False)
    pond_specific_project = PondSpecificProject.objects.filter(Q(project__in=private_project), Q(pond=request_user_ponds)).distinct()
    public_project = all_project.filter(is_public=True).distinct()
    list_project = list(public_project)
    for private_proj in pond_specific_project:
        list_project.append(private_proj.project)
    return list_project

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


def get_todays_milestones_json(user, current_projects):
    """
    Return todays milestone that are due for the given user
    :param user:
    :return:
    """
    milestone_list = []
    mil_list = get_todays_milestones(user, current_projects)
    for milestone in mil_list:
        milestone_list.append({
            'blurb':milestone.blurb,
            'id':milestone.id
        })
    return milestone_list


def get_recent_projects_json(projects):
    project_list = []
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


def generate_reset_code(user):
    old_pass_reset = PasswordReset.objects.filter(user=user)
    for each_set in old_pass_reset:
        each_set.delete()
    random_str = randomword(6)
    new_set = PasswordReset(user=user, token=random_str)
    new_set.save()
    return new_set.token


def reset_forget_password(user, token):
    try:
        new_set = PasswordReset.objects.get(user=user, token=token, is_active=True, was_used=False)
        new_set.is_active = False
        new_set.was_used = True
        new_set.save()
        return True
    except ObjectDoesNotExist:
        return False


def randomword(length):
   return ''.join(random.choice(string.lowercase) for i in range(length))


