from ..tasks.models import TikedgeUser, UserProject
from ..tasks.forms.form_module import get_current_datetime
from .models import ProfilePictures, ProgressVideoSet, ProgressVideo, Challenge, \
    Notification, VoucheMilestone, SeenMilestone, SeenProject, Follow, PondSpecificProject, \
     PondRequest, Pond, PondMembership, ProgressImpressedCount, PondProgressFeed, ProgressPictureSet, VoucheProject, LetDownProject, WorkEthicRank
from django.db.models import Q
from tasks_feed import NotificationFeed, AcceptanceFeed, RequestFeed
from django.core.exceptions import ObjectDoesNotExist
import global_variables
import StringIO
from PIL import Image, ImageFilter
from journal_feed import JournalFeed
from tasks_feed import PondFeed, VideoProgressFeed
from itertools import chain
from datetime import timedelta
from ..tasks.modules import utc_to_local, randomword
import base64
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
from django.core.files.base import ContentFile
from django.core.files import File
import subprocess
import os


CURRENT_URL = global_variables.CURRENT_URL


def resize_image(image_field, is_profile_pic=False):
    """
    Backend resizing of images to 480 * 320
    :param image_field:
    :param is_profile_pic:
    :return:
    """
    image_file = StringIO.StringIO(image_field.read())
    image = Image.open(image_file)
    max_size = (250, 250)
    if not is_profile_pic:
        # image = image.resize((161, 161), Image.ANTIALIAS)
    # else:
        image.thumbnail(max_size, Image.ANTIALIAS)
    imout = image.filter(ImageFilter.DETAIL)
    imout.save(image_file, 'JPEG', quality=90)
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
        try:
            seen_project = Follow.objects.get(tasks=project)
            for each_follow in seen_project.users.all():
                interest_feed.append({
                    'username':each_follow.user.username,
                    'first_name':each_follow.user.first_name,
                    'last_name':each_follow.user.last_name,
                    'slug':project.slug,
                    'blurb':project.blurb,
                    'is_deleted':project.is_deleted,
                    'user_id':project.user.user.id,
                    'proj_id':project.id,
                    'created':seen_project.latest_follow
                })
        except ObjectDoesNotExist:
            pass
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
    message = input_message(type_of_message, milestone, project)[0]
    return message


def input_message(type_of_message, milestone_name, project_name):
    if type_of_message == global_variables.MILESTONE:
        LIST_OF_RANDOM_MESSAGE = [
            'I created a new milestone named: %s, for this %s project' % (milestone_name, project_name),
        ]
    elif type_of_message == global_variables.BEFORE_PICTURE:
        LIST_OF_RANDOM_MESSAGE = [
            "I added a new before picture to %s milestone" % milestone_name,
        ]
    elif type_of_message == global_variables.AFTER_PICTURE:
        LIST_OF_RANDOM_MESSAGE = [
            "I added a new after picture to %s milestone" % milestone_name,
        ]
    else:
        LIST_OF_RANDOM_MESSAGE = [
            "Created a new project: %s." % project_name,
        ]
    return LIST_OF_RANDOM_MESSAGE


def get_user_journal_feed(tikege_user):
    journal_list = []
    journals = tikege_user.journalpost_set.all().order_by('-day_created')
    for journal in journals:
        journal_feed = JournalFeed(journal)
        journal_list.append(journal_feed)
        sorted(journal_list,  key=lambda x: int(x.feed_entry.day_entry), reverse=True)
    return journal_list


def get_users_feed(user):
    list_of_feed = []
    project_public = UserProject.objects.filter(Q(is_live=True),
                                                Q(is_deleted=False), Q(is_public=True)).order_by('-made_live')
    user_ponds = Pond.objects.filter(Q(pond_members__user=user), Q(is_deleted=False))
    pond_specific_project = PondSpecificProject.objects.filter(Q(pond__in=user_ponds)).\
        exclude(project__in=project_public).order_by('-project__made_live').distinct()
    project_feed = list(project_public)
    for each_proj in pond_specific_project:
        project_feed.append(each_proj.project)
    for each_proj_feed in project_feed:
        print "Project Name %s \n" % each_proj_feed.name_of_project
        feed = PondFeed(each_proj_feed, type_of_feed=global_variables.PROJECT, url_domain=CURRENT_URL)
        list_of_feed.append(feed)
        milestone_feed = each_proj_feed.milestone_set.filter(Q(is_deleted=False)).order_by('-created_date').distinct()
        for each_tasks in milestone_feed:
            feed = PondFeed(each_tasks, type_of_feed=global_variables.MILESTONE, url_domain=CURRENT_URL)
            list_of_feed.append(feed)
            picture_feed = each_tasks.pictureset_set.filter(
                ~Q(after_picture=None), Q(is_deleted=False)).order_by('-last_updated').distinct()
            print "these are pictures ", picture_feed
            for each_pic in picture_feed:
                feed = PondFeed(each_pic, type_of_feed=global_variables.PICTURE_SET, url_domain=CURRENT_URL)
                list_of_feed.append(feed)
        progress_set = ProgressPictureSet.objects.get(project=each_proj_feed)
        feed = PondFeed(progress_set, type_of_feed=global_variables.PROGRESS, url_domain=CURRENT_URL)
        list_of_feed.append(feed)
    sorted_list = sorted(list_of_feed, key=lambda x: x.created, reverse=True)
    return sorted_list


def get_users_feed_json(user, local_timezone='UTC', start_range=0, end_range=12):
    challenges = Challenge.objects.filter(Q(is_deleted=False),
                                          Q(is_public=True)).order_by('-created')[start_range:4*end_range]
    challenge_request = challenges.filter(Q(project__is_completed=False), Q(project__made_progress=False))
    challenge_videos = challenges.filter(Q(project__made_progress=True))
    video_feed_list = get_video_feed(challenge_videos, local_timezone=local_timezone)
    challenge_request_list = get_request_challenges(challenge_request, local_timezone=local_timezone)
    video_feed_list.extend(challenge_request_list)
    sorted_list = sorted(video_feed_list, key=lambda x: x['created_sec'], reverse=True)
    return sorted_list


def get_video_feed(challenges, local_timezone='UTC'):
    """
    Each challenge can be either a link to a celebration, a recent upload, a new challenge request, or an accepted
    challenge request.
    Terms to determine types of each request.
    Two categories are request and videos set feed

    :param challenges:
    :param local_timezone:
    :return:
    """
    feed_list = []
    for challenge in challenges:
        video_set = ProgressVideoSet.objects.get(challenge=challenge)
        type_of_feed = global_variables.VIDEO_SET
        if not challenge.project.is_completed:
            video_set = video_set.list_of_progress_videos.order_by('-created').first()
            type_of_feed = global_variables.RECENT_VIDEO_UPLOAD
        feed = VideoProgressFeed(video_set, type_of_feed=type_of_feed, url_domain=CURRENT_URL,
                                 local_timezone=local_timezone)
        feed_list.append(feed)
    return feed_list


def get_request_challenges(challenges, local_timezone='UTC'):
    """
    :param challenges:
    :param local_timezone:
    :return:
    """
    feed_list = []
    for challenge in challenges:
        if challenge.challenge_responded:
            challenge_feed = AcceptanceFeed(challenge, local_timezone=local_timezone)
        else:
            challenge_feed = RequestFeed(challenge, local_timezone=local_timezone)
        feed_list.append(challenge_feed.progress)
    return feed_list

'''
def get_users_feed_json(user, local_timezone='UTC'):
    list_of_feed = []
    list_of_feed_json = []
    project_public = UserProject.objects.filter(Q(is_deleted=False), Q(is_public=True)).order_by('-made_live')
    user_ponds = Pond.objects.filter(Q(pond_members__user=user), Q(is_deleted=False))
    pond_specific_project = PondSpecificProject.objects.filter(Q(pond__in=user_ponds), Q(project__is_deleted=False)).\
        exclude(project__in=project_public).order_by('-project__made_live').distinct()
    project_feed = list(project_public)

    for each_proj in pond_specific_project:
        project_feed.append(each_proj.project)
        print "pond project appended ", each_proj.project.name_of_project
    for each_proj_feed in project_feed:
        print "Project Name %s \n" % each_proj_feed.name_of_project
        feed = PondFeed(each_proj_feed, type_of_feed=global_variables.PROJECT, url_domain=CURRENT_URL)
        list_of_feed.append(feed)
        created_sec = int(feed.created.strftime('%s'))
        list_of_feed_json.append({
           'name': feed.task_owner_name,
           'is_picture_feed': False,
           'is_milestone_feed': False,
           'is_project_feed': True,
           'is_progress_feed': False,
           'message':feed.message,
           'project_slug':feed.tasks.slug,
           'is_active': feed.tasks.is_live,
           'follow_count':feed.follow_count,
            'vouch_count':feed.vouche_count,
           'seen_count': feed.seen_count,
           'created':utc_to_local(feed.created, local_timezone=local_timezone).strftime("%B %d %Y %I:%M %p"),
           'profile_url':feed.profile_url,
           'id': feed.tasks.id,
           'user_id':feed.feed_user.id,
           'is_completed':feed.tasks.is_completed,
           'is_failed':feed.tasks.is_failed,
           'created_sec':created_sec,
           'intro_video_url': feed.project_video_url()
        })
        video_set = ProgressVideoSet.objects.get(project=each_proj_feed)
        type_of_feed = global_variables.VIDEO_SET
        if not each_proj_feed.is_completed:
            video_set = video_set.list_of_progress_videos.order_by('created').first()
            type_of_feed = global_variables.RECENT_VIDEO_UPLOAD
        feed = VideoProgressFeed(video_set, type_of_feed=type_of_feed, url_domain=CURRENT_URL,
                                 local_timezone=local_timezone)
        if feed.progress:
            list_of_feed_json.append(feed.progress)
    sorted_list = sorted(list_of_feed_json, key=lambda x: x['created_sec'], reverse=True)
    return sorted_list
'''

def get_progress_set(progress_set, timezone):
    list_progress_entry = []
    for each_set in progress_set:
        set_dic = {'name_of_project':each_set.project.name_of_project, 'id':each_set.id, 'list_of_progress_pictures':[]}
        print "each prog ", each_set.list_of_progress_pictures.all()
        for each_progress in each_set.list_of_progress_pictures.all().filter(is_deleted=False):
            impressed = 0
            try:
                impressed = ProgressImpressedCount.objects.get(tasks=each_progress).get_count()
            except ObjectDoesNotExist:
                pass
            set_dic['list_of_progress_pictures'].append({
                'progress_message':each_progress.name_of_progress,
                'date_created': utc_to_local(each_progress.last_updated, local_timezone=timezone).strftime("%B %d %Y %I:%M %p"),
                'image_url': CURRENT_URL+each_progress.picture.url,
                'progress_id': each_progress.id,
                'impressed_by': impressed
            })
        if not each_set.is_empty:
            list_progress_entry.append(set_dic)
    return list_progress_entry


def get_picture_list_from_set(progress, timezone_, indi_proj=False):
    prog_list = []
    for each_progress in progress.list_of_progress_pictures.all().filter(is_deleted=False):
        impressed = 0
        try:
            impressed = ProgressImpressedCount.objects.get(tasks=each_progress).get_count()
        except ObjectDoesNotExist:
            pass
        created_sec = int(each_progress.created.strftime('%s'))
        prog_list.append({
            'progress_message':each_progress.name_of_progress,
            'date_created': utc_to_local(each_progress.last_updated, local_timezone=timezone_).strftime("%B %d %Y %I:%M %p"),
            'image_url': CURRENT_URL+each_progress.picture.url,
            'progress_id': each_progress.id,
            'impressed_by': impressed,
            'progress_set_id': ProgressPictureSet.objects.get(list_of_progress_pictures=each_progress).id,
            'created_sec': created_sec,
            'experience_with': get_experience_with(each_progress),
        })
    if indi_proj:
        new_prog = sorted(prog_list, key=lambda pond: pond['created_sec'])
    else:
        new_prog = sorted(prog_list, key=lambda pond: pond['created_sec'], reverse=True)
    return new_prog


def get_pic_list(pic_list):
    pic_list_arr = []
    for each_pic in pic_list:
        pic_list_arr.append({
            'picture_before':CURRENT_URL+each_pic.before_picture.milestone_pics.url,
            'picture_after':CURRENT_URL+each_pic.after_picture.milestone_pics.url
        })
    return pic_list_arr


def get_notifications_alert(user):
    notifications = user.notification_set.filter(read=False)
    nofication_feed = NotificationFeed(user, notifications)
    return nofication_feed.highlight_new_notification()


def get_tag_list(tags):
    """
    Returns list of tags
    :param tags:
    :return:
    """
    list_tag = []
    for t in tags:
        list_tag.append(t.name_of_tag)
    return list_tag


def mark_progress_as_deleted(project):
    progress = ProgressPictureSet.objects.get(project=project)
    progress.is_empty = True
    for pic in progress.list_of_progress_pictures.all():
        pic.is_deleted = True
        pic.save()


def create_failed_notification(milestone):
    yesterday = get_current_datetime() - timedelta(hours=18)
    if milestone.is_active and milestone.created_date < yesterday:
        if not milestone.is_completed:
            milestone.is_failed = True
        ponds = Pond.objects.filter(pond_members__user=milestone.user.user)
        try:
            vouches = VoucheMilestone.objects.get(tasks=milestone)
        except ObjectDoesNotExist:
            vouches = None
        mes = "%s %s quit on the milestone: %s" % (milestone.user.user.first_name, milestone.user.user.last_name,
                                                      milestone.name_of_milestone)
        if vouches:
            for each_user in vouches.users.all():

                new_notif = Notification(user=each_user.user, name_of_notification=mes, id_of_object=vouches.id,
                                         type_of_notification=global_variables.USER_DELETED_MILESTONE)
                new_notif.save()
        for each_pond in ponds:
            for each_user in each_pond.pond_members.all():

                new_notif = Notification(user=each_user.user, name_of_notification=mes,
                                         type_of_notification=global_variables.USER_DELETED_MILESTONE)
                print "stay there please ", new_notif.user.username
                new_notif.save()


def create_failed_notification_proj(project):
    yesterday = get_current_datetime() - timedelta(hours=18)
    if project.is_live and project.created < yesterday:
        project.is_failed = True
        ponds = Pond.objects.filter(pond_members__user=project.user.user)
        mes = "%s %s quit on the goal: %s" % (project.user.user.first_name, project.user.user.last_name,
                                                      project.name_of_project)
        for each_pond in ponds:
            for each_user in each_pond.pond_members.all():
                new_notif = Notification(user=each_user.user, id_of_object=project.id, name_of_notification=mes,
                                         type_of_notification=global_variables.USER_DELETED_PROJECT)
                new_notif.save()


def create_failed_notification_proj_by_deletion(project):
    yesterday = get_current_datetime() - timedelta(hours=18)
    if project.is_live and project.created < yesterday:
        project.is_failed = True
        ponds = Pond.objects.filter(pond_members__user=project.user.user)
        mes = "%s %s quit on the goal: %s" % (project.user.user.first_name, project.user.user.last_name,
                                                      project.name_of_project)
        vouches = VoucheProject.objects.get(tasks=project)
        if vouches.get_count():
            for each_user in vouches.users.all():
                new_notif = Notification(user=each_user.user, name_of_notification=mes,id_of_object=project.id,
                                         type_of_notification=global_variables.USER_DELETED_PROJECT)
                new_notif.save()

        for each_pond in ponds:
            for each_user in each_pond.pond_members.all():
                new_notif = Notification(user=each_user.user, name_of_notification=mes, id_of_object=vouches.id,
                                         type_of_notification=global_variables.USER_DELETED_PROJECT)
                new_notif.save()


def notification_exist(user):
    """
    Check if notification exist.
    :param user:
    :return:
    """
    return get_notifications_alert(user)


def file_is_picture(picture):
    picture_file = str(picture)
    if picture_file.lower().endswith(('png', 'jpg', 'jpeg', 'PNG', 'JPG', 'JPEG')):
        return True
    '''
    else:
        file_type = magic.from_file(picture)
        if ('PNG' in file_type or 'JPG' in file_type or 'JPEG' in file_type \
                or 'png' in file_type or 'jpg' in file_type or 'jpeg' in file_type):
            return True
    '''
    return False


def get_pond_profile(tikedge_users, owner):
    dict_list_of_pond = []
    for tikedge_user in tikedge_users:
        try:
            picture = ProfilePictures.objects.get(tikedge_user=tikedge_user, is_deleted=False)
            picture_url = CURRENT_URL+picture.profile_pics.url
        except ObjectDoesNotExist:
            picture_url = None
        if owner == tikedge_user:
           is_creator = True
        else:
            is_creator = False
        try:
            work_rank = WorkEthicRank.objects.get(tikedge_user=tikedge_user)
        except ObjectDoesNotExist:
            work_rank = WorkEthicRank(tikedge_user=tikedge_user)
            work_rank.save()
        dict_list_of_pond.append({
            'profile_pics_url':picture_url,
            'username':tikedge_user.user.username,
            'first_name':tikedge_user.user.first_name,
            'last_name':tikedge_user.user.last_name,
            'is_creator':is_creator,
            'id':tikedge_user.user.id,
            'rank': work_rank.work_ethic_rank
        })
    sorted_pond = sorted(dict_list_of_pond, key=lambda pond: pond['rank'], reverse=True)
    return sorted_pond


def get_all_pond_members(user):
    """
    Get the pond profile of all pond members associated with user
    :param user:
    :return:
    """
    pond_profile_list = []
    all_pond = get_pond(user)
    for each_pond in all_pond:
        pond_profiles = get_pond_profile(each_pond.pond_members.all(), each_pond.pond_creator)
        for each_person in pond_profiles:
            if each_person not in pond_profile_list and each_person['id'] != user.id:
                pond_profile_list.append(each_person)
    return pond_profile_list


def get_pond(user):
    ponds = Pond.objects.filter(pond_members__user=user, is_deleted=False)
    return ponds


def get_experience_with(progress):
    list_of_tikedge_users = []
    for each_user in progress.experience_with.all():
        list_of_tikedge_users.append({
            'first_name': each_user.user.first_name,
            'last_name': each_user.user.last_name,
            'id': each_user.id,
            'user_name':each_user.user.username
        })
    if not list_of_tikedge_users:
        return False
    return list_of_tikedge_users


def get_pond_feed(the_pond):
    pond_feeds = PondProgressFeed.objects.filter(pond=the_pond)
    pond_feed_list = []
    for each_item in pond_feeds:
        pond_feed_list.append({
            'name_of_feed':each_item.name_of_feed,
            'proj_id':each_item.project.id
        })
    return pond_feed_list


def new_goal_or_progress_added_notification_to_pond(project, is_new_project=True):
    """
    Send notification to all pond members about users activities
    :param project:
    :param is_new_project: type of notification either a new project(goal) or new progress
    :return:
    """
    pond_member_list = []
    pond_member_list.append(project.user)
    try:
        pond_specifics = PondSpecificProject.objects.get(project=project)
        ponds = pond_specifics.pond.filter(is_deleted=False)
    except ObjectDoesNotExist:
        ponds = get_pond(project.user.user)
    for each_pond in ponds:
        for each_member in each_pond.pond_members.all():
            if each_member not in pond_member_list:
                if is_new_project:
                    notif_mess = "Pond member %s %s created a new goal: %s" % \
                    (project.user.user.first_name, project.user.user.last_name, project.name_of_project)
                    new_notif = Notification(type_of_notification=global_variables.NEW_PROJECT_ADDED,id_of_object=project.id,
                                             name_of_notification=notif_mess, user=each_member.user)
                else:
                    notif_mess = "Pond member %s %s added a new progress to his goal: %s" % \
                    (project.user.user.first_name, project.user.user.last_name, project.name_of_project)
                    new_notif = Notification(type_of_notification=global_variables.NEW_PROGRESS_ADDED,id_of_object=project.id,
                                             name_of_notification=notif_mess, user=each_member.user)
                new_notif.save()
                pond_member_list.append(each_member)
    followers = Follow.objects.get(tasks=project).users.all()
    for each_member in followers:
        if each_member not in pond_member_list:
            notif_mess = "%s %s added a new progress to his goal: %s" % \
                            (project.user.user.first_name, project.user.user.last_name, project.name_of_project)
            new_notif = Notification(type_of_notification=global_variables.NEW_PROGRESS_ADDED,id_of_object=project.id,
                                                 name_of_notification=notif_mess, user=each_member.user)
            new_notif.save()
            pond_member_list.append(each_member)


def pond_to_json(ponds):
    pond_list = []
    for each_pond in ponds:
        try:
            profile_pic = ProfilePictures.objects.get(tikedge_user=each_pond.pond_creator, is_deleted=False)
            profile_pic_url = CURRENT_URL+profile_pic.profile_pics.url
        except ObjectDoesNotExist:
            profile_pic_url = None
        pond_list.append({
            "owner_profile_pic": profile_pic_url,
            "name": each_pond.name_of_pond,
            "id":each_pond.id
        })
    return pond_list


def get_let_down_notifications(user):
    """
    Get all the people that you let down
    :param user:
    :return:
    """
    tikedge_user = TikedgeUser.objects.get(user=user)
    user_project = tikedge_user.userproject_set.filter(is_deleted=False)
    let_down_list = []
    for each_proj in user_project:
        try:
            let_down = LetDownProject.objects.get(tasks=each_proj)
            count = let_down.get_count()
            mess = "You let down %d people by failing to complete this goal: %s.." % count, each_proj.blurb
            let_down_list.append({
                'name_of_blurb':mess,
                'proj':each_proj,
                'count':count,
                'created':let_down.latest_letDown,
                'id':each_proj.id,
                'first_name':None,
                'last_name':None

            })
        except ObjectDoesNotExist:
            pass
    sorted_let_down_list = sorted(let_down_list, key=lambda x: x["created"], reverse=True)
    return sorted_let_down_list


def get_notification_of_user(user, timezone='UTC'):
    try:
        tikedge_user = TikedgeUser.objects.get(user=user)
        print "tikdge name ", tikedge_user.user.username
        let_down = let_downs(user)
        proj_vouches = get_project_vouch_notifications(user)
        new_ponder = get_new_pond_member_notification(tikedge_user)
        interests = get_interest_notification(tikedge_user.userproject_set.all())
        quited_on_project = Notification.objects.filter(Q(user=user),
                                                          Q(type_of_notification=global_variables.USER_DELETED_PROJECT)).order_by('-created')
        ponder_request = PondRequest.objects.filter(Q(pond__pond_members__user=user), ~Q(user=tikedge_user)).order_by('-date_requested')
        notif_list = []
        for each_mil in let_down:
            created = int(each_mil['created'].strftime('%s'))
            notif_list.append({
                'blurb':each_mil['name_of_blurb'],
                'first_name':each_mil['first_name'],
                'last_name':each_mil['last_name'],
                'count': each_mil['count'],
                'created_view':utc_to_local(each_mil['created'], local_timezone=timezone).strftime("%B %d %Y %I:%M %p"),
                'is_let_down':True,
                'is_project_vouch':False,
                'is_new_ponder':False,
                'is_interests':False,
                'is_mil_quit': False,
                'is_proj_quit':False,
                'is_pond_request':False,
                'new_project':False,
                'new_progress':False,
                'progress_viewed':False,
                'project_viewed':False,
                'project_liked': False,
                'is_shared_exp':False,
                'id':each_mil['id'],
                'mil_is_deleted':each_mil['proj'].is_deleted,
                'created':created
            })
        for each_mil in proj_vouches:
            created = int(each_mil['created'].strftime('%s'))
            notif_list.append({
                'blurb':each_mil['blurb'],
                'is_let_down':False,
                'is_project_vouch':True,
                'is_new_ponder':False,
                'is_interests':False,
                'is_mil_quit': False,
                'is_proj_quit':False,
                'is_pond_request':False,
                'new_project':False,
                'new_progress':False,
                'progress_viewed':False,
                'project_viewed':False,
                'project_liked': False,
                'is_shared_exp':False,
                'id':each_mil['id'],
                'created':created,
                'proj_is_deleted':each_mil['is_proj_deleted'],
                'count': each_mil['count']
            })
        for each_mil in ponder_request:
            created = int(each_mil.date_requested.strftime('%s'))
            notif_list.append({
                'first_name':each_mil.user.user.first_name,
                'last_name':each_mil.user.user.last_name,
                'count': None,
                'is_let_down':False,
                'is_project_vouch':False,
                'is_new_ponder':False,
                'is_interests':False,
                'is_mil_quit': False,
                'is_proj_quit':False,
                'is_pond_request':True,
                'new_project':False,
                'new_progress':False,
                'progress_viewed':False,
                'project_viewed':False,
                'project_liked': False,
                'is_shared_exp':False,
                'id':each_mil.user.user.id,
                'pond_id':each_mil.pond.id,
                'request_id':each_mil.id,
                'request_accepted':each_mil.request_accepted,
                'created':created,
                'blurb':each_mil.pond.blurb,
                'is_pond_deleted':each_mil.pond.is_deleted,
                'request_responded_to': each_mil.request_responded_to,
                'request_denied':each_mil.request_denied
            })
        for each_mil in interests:
            created = int(each_mil['created'].strftime('%s'))
            notif_list.append({
                'blurb':each_mil['blurb'],
                'is_let_down':False,
                'is_project_vouch':False,
                'is_new_ponder':False,
                'is_interests':True,
                'is_mil_quit': False,
                'is_proj_quit':False,
                'is_pond_request':False,
                'new_project':False,
                'new_progress':False,
                'progress_viewed':False,
                'project_viewed':False,
                'project_liked': False,
                'is_shared_exp':False,
                'user_id':each_mil['user_id'],
                'proj_id':each_mil['proj_id'],
                'username':each_mil['username'],
                'first_name':each_mil['first_name'],
                'last_name':each_mil['last_name'],
                'is_deleted':each_mil['is_deleted'],
                'created':created

            })
        for each_mil in quited_on_project:
            created = int(each_mil.created.strftime('%s'))
            notif_list.append({
                'blurb':each_mil.name_of_notification,
                'is_let_down':False,
                'is_project_vouch':False,
                'is_new_ponder':False,
                'is_interests':False,
                'is_mil_quit': False,
                'is_proj_quit':True,
                'is_pond_request':False,
                'new_project':False,
                'new_progress':False,
                'progress_viewed':False,
                'project_viewed':False,
                'project_liked': False,
                'is_shared_exp':False,
                'created':created
            })
        for each_mil in new_ponder:
            created = int(each_mil.date_response.strftime('%s'))
            notif_list.append({
                'first_name':each_mil.user.user.first_name,
                'last_name':each_mil.user.user.last_name,
                'count': None,
                'is_let_down':False,
                'is_project_vouch':False,
                'is_new_ponder':True,
                'is_interests':False,
                'is_mil_quit': False,
                'is_proj_quit':False,
                'is_pond_request':False,
                'new_project':False,
                'new_progress':False,
                'progress_viewed':False,
                'project_viewed':False,
                'project_liked': False,
                'is_shared_exp':False,
                'is_deleted':each_mil.pond.is_deleted,
                'user_id':each_mil.user.user.id,
                'blurb':each_mil.pond.blurb,
                'pond_id':each_mil.pond.id,
                'created':created
            })
        notifications = Notification.objects.filter(user=user, type_of_notification=global_variables.NEW_SHARED_EXPERIENCE)
        for notif_mess in notifications:
            user_proj_id = notif_mess.id_of_object
            each_mil = UserProject.objects.get(id=user_proj_id)
            created = int(notif_mess.created.strftime('%s'))
            notif_list.append({
                'first_name':each_mil.user.user.first_name,
                'last_name':each_mil.user.user.last_name,
                'count': None,
                'is_let_down':False,
                'is_project_vouch':False,
                'is_new_ponder':False,
                'is_interests':False,
                'is_mil_quit': False,
                'is_proj_quit':False,
                'is_pond_request':False,
                'new_project':False,
                'new_progress':False,
                'progress_viewed':False,
                'project_viewed':False,
                'is_shared_exp':True,
                'is_deleted':each_mil.is_deleted,
                'project_liked': False,
                'user_id':each_mil.user.user.id,
                'blurb':notif_mess.name_of_notification,
                'id':each_mil.id,
                'created':created,
            })

        notifications = Notification.objects.filter(user=user, type_of_notification=global_variables.NEW_PROJECT_ADDED)
        for notif_mess in notifications:
            user_proj_id = notif_mess.id_of_object
            try:
                each_mil = UserProject.objects.get(id=user_proj_id)
                created = int(notif_mess.created.strftime('%s'))
                notif_list.append({
                    'first_name':each_mil.user.user.first_name,
                    'last_name':each_mil.user.user.last_name,
                    'count': None,
                    'is_let_down':False,
                    'is_project_vouch':False,
                    'is_new_ponder':False,
                    'is_interests':False,
                    'is_mil_quit': False,
                    'is_proj_quit':False,
                    'is_pond_request':False,
                    'new_project':True,
                    'new_progress':False,
                    'progress_viewed':False,
                    'project_viewed':False,
                    'is_deleted':each_mil.is_deleted,
                    'project_liked': False,
                    'is_shared_exp':False,
                    'user_id':each_mil.user.user.id,
                    'blurb':notif_mess.name_of_notification,
                    'id':each_mil.id,
                    'created':created,

                })
            except ObjectDoesNotExist:
                pass
        notifications = Notification.objects.filter(user=user, type_of_notification=global_variables.PROJECT_WAS_VIEWED)
        for notif_mess in notifications:
            try:
                each_mil = UserProject.objects.get(id=int(notif_mess.id_of_object))
                created = int(notif_mess.created.strftime('%s'))
                notif_list.append({
                    'first_name':each_mil.user.user.first_name,
                    'last_name':each_mil.user.user.last_name,
                    'count': None,
                    'is_let_down':False,
                    'is_project_vouch':False,
                    'is_new_ponder':False,
                    'is_interests':False,
                    'is_mil_quit': False,
                    'is_proj_quit':False,
                    'is_pond_request':False,
                    'new_project':False,
                    'new_progress':False,
                    'progress_viewed':False,
                    'project_viewed':True,
                    'is_deleted':each_mil.is_deleted,
                    'project_liked': False,
                    'is_shared_exp':False,
                    'user_id':each_mil.user.user.id,
                    'blurb':notif_mess.name_of_notification,
                    'id':each_mil.id,
                    'created':created
                })
            except ObjectDoesNotExist:
                pass
        notifications = Notification.objects.filter(user=user, type_of_notification=global_variables.NEW_PROGRESS_ADDED)
        for notif_mess in notifications:
            print "Hey new pond added \n"
            try:
                each_mil = UserProject.objects.get(id=int(notif_mess.id_of_object))
                created = int(notif_mess.created.strftime('%s'))
                notif_list.append({
                    'first_name':each_mil.user.user.first_name,
                    'last_name':each_mil.user.user.last_name,
                    'count': None,
                    'is_let_down':False,
                    'is_project_vouch':False,
                    'is_new_ponder':False,
                    'is_interests':False,
                    'is_mil_quit': False,
                    'is_proj_quit':False,
                    'is_pond_request':False,
                    'new_project':False,
                    'new_progress':True,
                    'progress_viewed':False,
                    'project_viewed':False,
                    'is_deleted':each_mil.is_deleted,
                    'project_liked': False,
                    'is_shared_exp':False,
                    'user_id':each_mil.user.user.id,
                    'blurb':notif_mess.name_of_notification,
                    'id':each_mil.id,
                    'created':created
                })
            except ObjectDoesNotExist:
                pass
            notifications = Notification.objects.filter(user=user, type_of_notification=global_variables.PROGRESS_WAS_VIEWED)
            for notif_mess in notifications:
                try:
                    each_mil = UserProject.objects.get(id=int(notif_mess.id_of_object))
                    created = int(notif_mess.created.strftime('%s'))
                    notif_list.append({
                        'first_name':each_mil.user.user.first_name,
                        'last_name':each_mil.user.user.last_name,
                        'count': None,
                        'is_let_down':False,
                        'is_project_vouch':False,
                        'is_new_ponder':False,
                        'is_interests':False,
                        'is_mil_quit': False,
                        'is_proj_quit':False,
                        'is_pond_request':False,
                        'new_project':False,
                        'new_progress':False,
                        'progress_viewed':True,
                        'project_viewed':False,
                        'is_deleted':each_mil.is_deleted,
                        'project_liked': False,
                        'is_shared_exp':False,
                        'user_id':each_mil.user.user.id,
                        'blurb':notif_mess.name_of_notification,
                        'id':each_mil.id,
                        'created':created
                    })
                except ObjectDoesNotExist:
                    pass
            notifications = Notification.objects.filter(user=user,
                                                      type_of_notification=global_variables.PROGRESS_WAS_IMPRESSED)
            for notif_mess in notifications:
                try:
                    each_mil = UserProject.objects.get(id=int(notif_mess.id_of_object))
                    created = int(notif_mess.created.strftime('%s'))
                    notif_list.append({
                        'first_name':each_mil.user.user.first_name,
                        'last_name':each_mil.user.user.last_name,
                        'count': None,
                        'is_let_down':False,
                        'is_project_vouch':False,
                        'is_new_ponder':False,
                        'is_interests':False,
                        'is_mil_quit': False,
                        'is_proj_quit':False,
                        'is_pond_request':False,
                        'new_project':False,
                        'new_progress':False,
                        'progress_viewed':False,
                        'project_viewed':False,
                        'project_liked': True,
                        'is_shared_exp':False,
                        'is_deleted':each_mil.is_deleted,
                        'user_id':each_mil.user.user.id,
                        'blurb':notif_mess.name_of_notification,
                        'id':each_mil.id,
                        'created':created
                    })
                except ObjectDoesNotExist:
                    pass
        sort_notif_list = sorted(notif_list, key=lambda x: x['created'], reverse=True)
        return sort_notif_list
    except None:
        return []


def project_viewed_notifications(user):
    """
    Get all new notifications related to new project
    :param user:
    :return:
    """
    project_view_notifications = user.notification_set.all().filter(Q(user=user,
                                                               type_of_notification=global_variables.PROJECT_WAS_VIEWED))
    project_proj_list = []
    for each_prog in project_view_notifications:
        try:
            project = UserProject.objects.get(is_deleted=False, id=each_prog.id_of_object)
            project_proj_list.append(project)
        except ObjectDoesNotExist:
            pass
    return project_proj_list


def progress_viewed_notifications(user):
    """
    Get all new notifications related to new progress
    :param user:
    :return:
    """
    progress_view_notifications = user.notification_set.all().filter(Q(user=user,
                                                               type_of_notification=global_variables.PROGRESS_WAS_VIEWED))
    progress_proj_list = []
    for each_prog in progress_view_notifications:
        try:
            project = UserProject.objects.get(is_deleted=False, id=each_prog.id_of_object)
            progress_proj_list.append(project)
        except ObjectDoesNotExist:
            pass
    return progress_proj_list


def project_added_notifications(user):
    """
    Get all new notifications related to new project
    :param user:
    :return:
    """
    project_view_notifications = user.notification_set.all().filter(Q(user=user,
                                                               type_of_notification=global_variables.NEW_PROJECT_ADDED))
    project_proj_list = []
    for each_prog in project_view_notifications:
        try:
            project = UserProject.objects.get(is_deleted=False, id=each_prog.id_of_object)
            project_proj_list.append(project)
        except ObjectDoesNotExist:
            pass
    return project_proj_list


def progress_added_notifications(user):
    """
    Get all new notifications related to new progress
    :param user:
    :return:
    """
    progress_view_notifications = user.notification_set.all().filter(Q(user=user,
                                                               type_of_notification=global_variables.NEW_PROGRESS_ADDED))
    progress_proj_list = []
    for each_prog in progress_view_notifications:
        try:
            project = UserProject.objects.get(is_deleted=False, id=each_prog.id_of_object)
            progress_proj_list.append(project)
        except ObjectDoesNotExist:
            pass
    return progress_proj_list


def progress_latest_impressed(user):
    """
    Get all new notifications related to new progress_like
    :param user:
    :return:
    """
    progress_liked_notifications = user.notification_set.all().filter(Q(user=user,
                                                               type_of_notification=global_variables.PROGRESS_WAS_IMPRESSED))
    progress_impress_list = []
    for each_prog in progress_liked_notifications:
        try:
            project = UserProject.objects.get(is_deleted=False, id=each_prog.id_of_object)
            progress_impress_list.append(project)
        except ObjectDoesNotExist:
            pass
    return progress_impress_list


def notification_of_people_that_let_you_down(user):
    """
    Get all people that let you down
    :param user:
    :return:
    """
    let_down = LetDownProject.objects.filter(users__user=user)
    let_down_list = []
    for each_proj in let_down:
        try:
            notifications = Notification.objects.filter(id_of_object=each_proj.id)
            for each_notif in notifications:
                let_down_list.append({
                    'name_of_blurb':each_notif.name_of_notification,
                    'proj':each_proj.tasks,
                    'count': -1,
                    'created':each_notif.created,
                    'id':each_proj.tasks.id,
                    'first_name':each_proj.tasks.user.user.first_name,
                    'last_name':each_proj.tasks.user.user.last_name
                })
        except ObjectDoesNotExist:
            pass
    sorted_let_down_list = sorted(let_down_list, key=lambda x: x['created'], reverse=True)
    return sorted_let_down_list


def let_downs(user):
    let_down_list = get_let_down_notifications(user) + notification_of_people_that_let_you_down(user)
    sorted_let_downs = sorted(let_down_list, key=lambda x: x['created'], reverse=True)
    return sorted_let_downs


def get_milestone_vouch_notifications(user):
    tikedge_user = TikedgeUser.objects.get(user=user)
    milestones = tikedge_user.milestone_set.filter(is_deleted=False)
    mil_vouch_list = []
    for each_mil in milestones:
        print " each mil", each_mil
        try:
            mil_vouch = VoucheMilestone.objects.get(tasks=each_mil)
            count = mil_vouch.users.count()
            mil_vouch_list.append({
                'blurb':each_mil.blurb,
                'slug':each_mil.slug,
                'count':count,
                'id':each_mil.id,
                'created':mil_vouch.latest_vouch,
                'is_mil_deleted':each_mil.is_deleted
            })
        except ObjectDoesNotExist:
            pass
    return mil_vouch_list


def get_project_vouch_notifications(user):
    tikedge_user = TikedgeUser.objects.get(user=user)
    user_projects = tikedge_user.userproject_set.filter(is_deleted=False)
    proj_vouch_list = []
    for each_proj in user_projects:
        print " each mil", each_proj
        proj_vouch = VoucheProject.objects.get(tasks=each_proj)
        count = proj_vouch.users.count()
        try:
            notifications = Notification.objects.filter(id_of_object=proj_vouch.id)
            for each_notif in notifications:
                proj_vouch_list.append({
                    'blurb':each_notif.name_of_notification,
                    'slug':each_proj.slug,
                    'count':count,
                    'id':each_proj.id,
                    'created':each_notif.created,
                    'is_proj_deleted':each_proj.is_deleted
                })
        except ObjectDoesNotExist:
            pass
    return proj_vouch_list


def milestone_project_app_view(milestones):
    mil_list = []
    for each_mil in milestones:
        mil_list.append({
            'id':each_mil.id,
            'blurb':each_mil.blurb
        })
    return mil_list


def motivation_for_project_app_view(motivation):
    motif_list = []
    for each_motif in motivation:
        motif_list.append(
            each_motif.name_of_tag
        )
    return motif_list


def pond_for_project_app_view(pond_specific):
    if pond_specific:
        pond_list = {
            'blurb':pond_specific.pond.blurb,
            'id':pond_specific.pond.id
        }
    else:
        pond_list = None
    return pond_list


def send_pond_request(pond, user):
    tikedge_user = TikedgeUser.objects.get(user=user)
    data = {}
    try:
       PondRequest.objects.get(pond=pond, user=tikedge_user, request_responded_to=False)
       data['status'] = False
       data['error'] = "Chill! Request Already Sent!"
    except ObjectDoesNotExist:
       new_pond_request = PondRequest(pond=pond, user=tikedge_user)
       new_pond_request.save()
       pond_mess = "%s %s wants to join this pond: %s" % (tikedge_user.user.first_name,
                                                         tikedge_user.user.first_name, pond.name_of_pond)
       for member in pond.pond_members.all():
           notification = Notification(user=member.user, name_of_notification=pond_mess, id_of_object=new_pond_request.id,
                                       type_of_notification=global_variables.POND_REQUEST)
           notification.save()
       data['status'] = True
    return data


def available_ponds(tikedge_user, owner):
    """
    The available ponds of a user that they can add other user to.
    :param tikedge_user: the user to be added
    :param owner: the user doing the adding
    :return:
    """
    aval_ponds_list = []
    aval_ponds = get_pond(owner)
    for each_aval in aval_ponds:
        if tikedge_user not in each_aval.pond_members.all():
            aval_ponds_list.append(each_aval)
    return aval_ponds_list


def available_ponds_json(tikedge_user, owner):
    """
        The available ponds of a user that they can add other user to.
        :param tikedge_user: the user to be added
        :param owner: the user doing the adding
        :return:
        """
    aval_ponds_list = []
    aval_ponds = get_pond(owner)
    for each_aval in aval_ponds:
        if tikedge_user not in each_aval.pond_members.all():
            aval_ponds_list.append({
                'blurb':each_aval.blurb,
                'id':each_aval.id
            })
    return aval_ponds_list


def get_new_pond_member_notification(tikedge_user):
    pond_request_list = []
    pond = Pond.objects.filter(pond_members__user=tikedge_user.user, is_deleted=False)
    for each_pond in pond:
        pond_membership = PondMembership.objects.get(user=tikedge_user, pond=each_pond, date_removed=None)
        pond_requests = each_pond.pondrequest_set.all().filter(request_accepted=True, pond__pond_members=tikedge_user,
                                                               date_response__gte=pond_membership.date_joined)

        pond_request_list  = list(chain(pond_request_list, pond_requests))
    return pond_request_list


def mark_pond_request_notification_as_read(user):
    """
    Notification for new user requesting to join pond marked as read
    :param user:
    :return:
    """
    notifcation = user.notification_set.all().filter(read=False, type_of_notification=global_variables.POND_REQUEST)
    for each_notif in notifcation:
        each_notif.read = True
        each_notif.save()


def mark_new_ponder_notification_as_read(user):
    """
    Notification for a new user that has been added to pond marked as read
    :param user:
    :return:
    """
    notifcation = user.notification_set.all().filter(read=False, type_of_notification=global_variables.NEW_PONDERS)
    for each_notif in notifcation:
        each_notif.read = True
        each_notif.save()


def mark_milestone_vouch_as_read(user):
    """
    Noftication for a new vouch on milestone marked as read
    :param user:
    :return:
    """
    notifcation = user.notification_set.all().filter(read=False,
                                                     type_of_notification=global_variables.NEW_MILESTONE_VOUCH)
    for each_notif in notifcation:
        each_notif.read = True
        each_notif.save()


def mark_milestone_failed_as_read(user):
    """
    Noftication for a new vouch on milestone marked as read
    :param user:
    :return:
    """
    notifcation = user.notification_set.all().filter(read=False,
                                                     type_of_notification=global_variables.USER_DELETED_MILESTONE)
    for each_notif in notifcation:
        each_notif.read = True
        each_notif.save()


def mark_project_failed_as_read(user):
    """
    Noftication for a new vouch on milestone marked as read
    :param user:
    :return:
    """
    notifcation = user.notification_set.all().filter(read=False,
                                                     type_of_notification=global_variables.USER_DELETED_PROJECT)
    for each_notif in notifcation:
        each_notif.read = True
        each_notif.save()


def mark_milestone_pond_request_accepted_as_read(user):
    """
    Nofication that one has been accepted in a pond marked as read
    :param user:
    :return:
    """
    notifcation = user.notification_set.all().filter(read=False,
                                                     type_of_notification=global_variables.POND_REQUEST_ACCEPTED)
    for each_notif in notifcation:
        each_notif.read = True
        each_notif.save()


def mark_new_project_interested_as_read(user):
    """
    Notifciation that one has a new interest/follower of their project marked as read
    :param user:
    :return:
    """
    notifcation = user.notification_set.all().filter(read=False,
                                                     type_of_notification=global_variables.NEW_PROJECT_INTERESTED)
    for each_notif in notifcation:
        each_notif.read = True
        each_notif.save()


def mark_milestone_let_down_as_read(user):

    """
    Notification that one who failed to complete a set milestone/project let down a vouchers marked as read
    :param user:
    :return:
    """
    notifcation = user.notification_set.all().filter(read=False,
                                                     type_of_notification=global_variables.NEW_PROJECT_LETDOWN)
    for each_notif in notifcation:
        each_notif.read = True
        each_notif.save()


def mark_project_viewed(user):

    """
    Notification that people are looking at your goals marked as read
    :param user:
    :return:
    """
    notifcation = user.notification_set.all().filter(read=False,
                                                     type_of_notification=global_variables.PROJECT_WAS_VIEWED)
    for each_notif in notifcation:
        each_notif.read = True
        each_notif.save()


def mark_goal_let_down_as_read(user):
    """
    Notification that people are looking at your goals marked as read
    :param user:
    :return:
    """
    notifcation = user.notification_set.all().filter(read=False,
                                                     type_of_notification=global_variables.NEW_PROJECT_LETDOWN)
    for each_notif in notifcation:
        each_notif.read = True
        each_notif.save()


def mark_project_vouch_as_read(user):
    """
    Notification that people believe you will complete the goal as read
    :param user:
    :return:
    """
    notifcation = user.notification_set.all().filter(read=False,
                                                     type_of_notification=global_variables.NEW_PROJECT_VOUCH)
    for each_notif in notifcation:
        each_notif.read = True
        each_notif.save()


def mark_progress_impressed_as_read(user):
    """
    Notification that people liked a progress you made on your goal marked as read
    :param user:
    :return:
    """
    notifcation = user.notification_set.all().filter(read=False,
                                                     type_of_notification=global_variables.PROGRESS_WAS_IMPRESSED)
    for each_notif in notifcation:
        each_notif.read = True
        each_notif.save()


def mark_progress_viewed(user):

    """
    Notification that people are looking at your goal progress marked as read
    :param user:
    :return:
    """
    notifcation = user.notification_set.all().filter(read=False,
                                                     type_of_notification=global_variables.PROGRESS_WAS_VIEWED)
    for each_notif in notifcation:
        each_notif.read = True
        each_notif.save()


def mark_new_progress_added_as_read(user):

    """
    Notification that new progress has been created and has been read
    :param user:
    :return:
    """
    notifcation = user.notification_set.all().filter(read=False,
                                                     type_of_notification=global_variables.NEW_PROGRESS_ADDED)
    for each_notif in notifcation:
        each_notif.read = True
        each_notif.save()


def mark_new_project_added_as_read(user):

    """
    Notification that new project has been created and has been read
    :param user:
    :return:
    """
    notifcation = user.notification_set.all().filter(read=False,
                                                     type_of_notification=global_variables.NEW_PROJECT_ADDED)
    for each_notif in notifcation:
        each_notif.read = True
        each_notif.save()


def mark_shared_experience_as_read(user):

    """
    Notification that shared experience has been created and has been read
    :param user:
    :return:
    """
    notifcation = user.notification_set.all().filter(read=False,
                                                     type_of_notification=global_variables.NEW_SHARED_EXPERIENCE)
    for each_notif in notifcation:
        each_notif.read = True
        each_notif.save()


def get_picture_from_base64(data):
        """
        Convert from base64 to file
        :param self:
        :param data:
        :return:
        """
        if isinstance(data, basestring) and data.startswith('data:image'):
            # base64 encoded image - decode
            format, imgstr = data.split(';base64,')  # format ~= data:image/X,
            ext = format.split('/')[-1]  # guess file extension
            ran_word = randomword(12)
            data = ContentFile(base64.b64decode(imgstr), name='temp' + ran_word + '.' + ext)
            return data
        return False


def get_video_from_base64(data):
    """
    Convert from base64 to file
    :param self:
    :param data:
    :return:
    """
    if isinstance(data, basestring) and data.startswith('data:video'):
        # base64 encoded image - decode
        format, imgstr = data.split(';base64,')  # format ~= data:image/X,
        ext = format.split('/')[-1]  # guess file extension [data:video, quicktime]
        if ext == 'quicktime':
            ext = 'mov'
        ran_word = randomword(12)
        data = ContentFile(base64.b64decode(imgstr), name='temp' + ran_word + '.' + ext)
        return data
    return False


def convert_video_to_mp4(non_mp4_file, output_filename):
    process = subprocess.Popen(['ffmpeg', '-i', non_mp4_file, output_filename], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.stdin.write('Y')
    has_error = process.communicate()[0]
    if has_error:
        return False
    return True


def convert_to_mp4_file_for_file_object(video):
    filepath = video.video.url
    if not filepath.endswith(".mp4"):
        new_mp4_path = randomword(25)+".mp4"
        did_convert = convert_video_to_mp4(filepath, new_mp4_path)
        if did_convert:
            path_object = open(new_mp4_path)
            data = File(path_object)
            video.video.save(new_mp4_path, data)
            vid_name = "%s_%s" % (video.name_of_progress, str(new_mp4_path))
            video.video_name = vid_name
            video.save()


def upload_video_file(filepath, video_model):
    data = open(filepath)
    random_name = randomword(15) + str(filepath)
    video_model.video.save(random_name, data, save=False)
    return random_name


def make_timeline_video(progress_set):
    video_clips = []
    for each_prog in progress_set.list_of_progress_videos.all():
        file_ = VideoFileClip(each_prog.video.url)
        txt_clip = TextClip(each_prog.name_of_progress, fontsize=20, color='white')
        txt_clip = txt_clip.set_pos(('center','top')).set_duration(file_.duration)
        video = CompositeVideoClip([file_, txt_clip])
        video_clips.append(video)
    final_clips = concatenate_videoclips(video_clips)
    final_clips_name = progress_set.project.name_of_project + randomword(12) + ".mp4"
    temp_audio_name = progress_set.project.name_of_project + randomword(12) + ".mp3"
    abs_path = os.path.join(os.path.abspath('/tmp/'), final_clips_name)
    abs_audio_name = os.path.join(os.path.abspath('/tmp/'), temp_audio_name)
    final_clips.write_videofile(abs_path, temp_audiofile=abs_audio_name)
    f = open(abs_path)
    progress_set.video_timeline.save(abs_path, File(f))


