from django.shortcuts import render
from django.views.generic import View, FormView
from forms import tasks_forms
from models import User, TikedgeUser, UserProject,Milestone, TagNames, LaunchEmail
from tasks import begin_timeline_video
from ..social.models import ProfilePictures, JournalPost, PondSpecificProject, \
    Pond, ProgressPictureSet, VoucheProject, Follow, SeenProject, WorkEthicRank, ProgressVideoSet, ProjectVideo
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from datetime import timedelta
from ..social.modules import get_journal_message, \
    resize_image, available_ponds_json, create_failed_notification, \
    create_failed_notification_proj_by_deletion, get_picture_from_base64, mark_progress_as_deleted, \
    new_goal_or_progress_added_notification_to_pond, get_video_from_base64, upload_video_file, make_timeline_video
from modules import get_user_projects, \
    time_has_past, convert_html_to_datetime,\
    get_todays_milestones_json, \
    confirm_expired_project, get_completed_mil_count, get_completed_proj_count, get_failed_mil_count, \
    get_failed_proj_count, get_recent_projects_json, get_status, display_error, api_get_user_projects, get_profile_pic_json, \
    get_recent_projects

from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from datetime import datetime
from ..social.global_variables import MILESTONE, PROJECT, ALL_POND_STATUS
from friendship.models import Friend
import json
from django.contrib import messages
from braces.views import LoginRequiredMixin
from global_variables_tasks import CUSTOMER_SERVICE_EMAIL
from .forms import launch_form
import modules
from forms.form_module import get_current_datetime
from django.db.models import Q
import pytz
from tzlocal import get_localzone
from notification_keys import TOKEN_FOR_NOTIFICATION
from templated_email import send_templated_mail


class CSRFExemptView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CSRFExemptView, self).dispatch(*args, **kwargs)


class CSRFEnsureCookiesView(View):
    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super(CSRFEnsureCookiesView, self).dispatch(*args, **kwargs)


class ApiLoginView(CSRFExemptView):

    def post(self, request,  *args, **kwargs):
        response_data ={}
        username = request.POST.get('username')
        password = request.POST.get('password')
        print "name: %s password: %s" % (username, password)
        user = authenticate(username=username.strip(), password=password.strip())
        if user:
            if not user.is_active:
                user.is_active = True
                user.save()
            login(self.request, user)
            response_data['status'] = True
            login(self.request, user)
        else:
            response_data['error'] = "Username or Password is Invalid"
            response_data['status'] = False
        return HttpResponse(json.dumps(response_data), status=201)


class ApiRegistrationView(CSRFExemptView):

    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
         user_name = request.POST.get('username')
         password = request.POST.get('password')
         email = request.POST.get('email')
         first_name = request.POST.get('first_name')
         last_name = request.POST.get('last_name')
         response_data = {}
         response_data['success'] = "Name is not valid!"
         print "username %s password %s email %s first_name %s last_name %s" % (user_name, password, email, first_name, last_name)
         try:
             User.objects.get(username=user_name)
             response_data['success'] = "User name already exist"
         except ObjectDoesNotExist:
            try:
                User.objects.get(email=email)
                response_data['success'] = "Email already exist"
            except ObjectDoesNotExist:
                response_data['success'] = "created"
                user = User.objects.create_user(username=user_name, password=password, email=email, first_name=first_name,
                                            last_name=last_name)
                user.save()
                tickedge_user = TikedgeUser(user=user)
                tickedge_user.save()
                work_ethic_rank = WorkEthicRank(tikedge_user=tickedge_user)
                work_ethic_rank.save()
         response = HttpResponse(json.dumps(response_data), status=201)
         return response


class ApiGetPostInfo(CSRFExemptView):

    def get(self, request, *args, **kwargs):
        response = {}
        response["pond"] = {'status':False}
        username = request.GET.get("username")
        user = User.objects.get(username=username)
        user_ponds = Pond.objects.filter(Q(pond_members__user=user), Q(is_deleted=False))
        pond_list = []
        for user_pond in user_ponds:
            pond_list.append(
                    {'pond_name':user_pond.name_of_pond,
                        'id':user_pond.id
                    })
        if pond_list:
            response["pond"]["status"] = True
            response["pond"]["ponds"] = pond_list
        user_project = api_get_user_projects(user)
        response["user_project"] = {'status':False}
        if user_project:
            response["user_project"]["status"] = True
            response["user_project"]["projects"] = user_project
        return HttpResponse(json.dumps(response), status=201)


class ApiNewMilestone(CSRFExemptView):

    def post(self, request, *args, **kwargs):
        response = {}
        try:
            username = request.POST.get("username")
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            response["status"] = False
            response["error"] = "Log back In!"
            return HttpResponse(json.dumps(response), status=201)
        tikedge_user = TikedgeUser.objects.get(user=user)
        name_of_milestone= request.POST.get('milestone_name')
        name_of_project = request.POST.get('name_of_mil_proj')
        length_of_time = request.POST.get('length_of_time')
        valid_milestone_word = modules.check_milestone_word_is_valid(name_of_milestone)
        valid_project_name = modules.check_milestone_word_is_valid(name_of_project)
        if not valid_milestone_word:
            response["status"] = False
            response["error"] = "Words must be between 0 and 600!"
            return HttpResponse(json.dumps(response), status=201)
        if not valid_project_name:
            response["status"] = False
            response["error"] = "Milestone must be part of project!"
            return HttpResponse(json.dumps(response), status=201)
        timezone = request.POST.get('timezone')
        done_by = convert_html_to_datetime(request.POST.get('milestone_date'), timezone=timezone)
        if done_by:
            if time_has_past(done_by, timezone=timezone):
                response["status"] = False
                response["error"] = "The time for milestone completion has past!"
                return HttpResponse(json.dumps(response), status=201)
        else:
            response["status"] = False
            response["error"] = "Your date input seems to be wrong!"
            return HttpResponse(json.dumps(response), status=201)
        user_project = UserProject.objects.get(id=name_of_project, user=tikedge_user)
        print "Hey Milestone why don't you work ", length_of_time
        if len(length_of_time) != 0 and length_of_time != '-1':
                start_time = done_by - timedelta(hours=int(length_of_time))
                if time_has_past(start_time, timezone=timezone):
                    response["status"] = False
                    response["error"] = "The time for milestone completion has past!"
                    return HttpResponse(json.dumps(response), status=201)
        else:
            start_time = done_by - timedelta(minutes=20)
            if time_has_past(start_time, timezone=timezone):
                start_time = get_current_datetime() + timedelta(minutes=int(3))
                if start_time >= done_by:
                    response["status"] = False
                    response["error"] = "The time for milestone completion is not enough!"
                    return HttpResponse(json.dumps(response), status=201)
                        
        if user_project.length_of_project >= done_by:
            print start_time," motor", done_by
            new_milestone = Milestone(name_of_milestone=name_of_milestone, user=tikedge_user, reminder=start_time,
                                  done_by=done_by, project=user_project)

            new_milestone.save()
            day_entry = tikedge_user.journalpost_set.all().count()
            new_journal_entry = JournalPost(entry_blurb=get_journal_message(MILESTONE,
                                                                            milestone=new_milestone.blurb,
                                                                            project=user_project.blurb),
                                                                            day_entry=day_entry + 1,
                                                                            event_type=MILESTONE,
                                                                            is_milestone_entry=True,
                                                                            milestone_entry=new_milestone,
                                                                            user=tikedge_user,
                                                                         )
            new_journal_entry.save()
            response["status"] = True
            return HttpResponse(json.dumps(response), status=201)
        else:
            response["status"] = False
            response["error"] = "Hey, can't fit this milestone into the project scope!"
            return HttpResponse(json.dumps(response), status=201)


class ApiNewProject(CSRFExemptView):

    def post(self, request, *args, **kwargs):
        response = {}
        try:
            username = request.POST.get("username")
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            response["status"] = False
            response["error"] = "Log Back In! Try Again!"
            return HttpResponse(json.dumps(response), status=201)
        user_ponds = Pond.objects.filter(Q(pond_members__user=user), Q(is_deleted=False))
        name_of_project = request.POST.get('name_of_project')
        valid_project_name_entry = modules.check_milestone_word_is_valid(name_of_project)
        project_public_status = request.POST.get('public_status')
        print "public status %s " % project_public_status
        tags_obj = request.POST.get('tags')
        tags = tags_obj.split(",")

        if not valid_project_name_entry:
            response["status"] = False
            response["error"] = "Words must be between 0 and 600!"
            return HttpResponse(json.dumps(response), status=201)
        conver_date = request.POST.get('milestone_date')
        print "date_ for api new proj ", conver_date
        timezone = request.POST.get("timezone")
        if conver_date:
            end_by = convert_html_to_datetime(conver_date, timezone=timezone)
        else:
            response["status"] = False
            response["error"] = "It seems like your date input is wrong!"
            return HttpResponse(json.dumps(response), status=201)
        timezone = request.POST.get('timezone')
        if time_has_past(end_by, timezone=timezone):
            response["status"] = False
            response["error"] = "It seems like your date input is in the past!"
            return HttpResponse(json.dumps(response), status=201)
        tikedge_user = TikedgeUser.objects.get(user=user)
        new_project = UserProject(name_of_project=name_of_project, is_live=True,
                                  made_live=datetime.now(), user=tikedge_user, length_of_project=end_by)
        new_project.save()
        try:
            if len(tags_obj) > 0:
                for item in tags:
                    try:
                        item_obj = TagNames.objects.get(name_of_tag=item)
                    except ObjectDoesNotExist:
                        item_obj = TagNames(name_of_tag=item)
                        item_obj.save()
                    new_project.tags.add(item_obj)
                new_project.save()
        except ValueError:
            pass
        day_entry = tikedge_user.journalpost_set.all().count()
        new_journal_entry = JournalPost(
                                        entry_blurb=get_journal_message(PROJECT, project=new_project.blurb),
                                        day_entry=day_entry + 1,
                                        event_type=PROJECT,
                                        is_project_entry=True,
                                        new_project_entry=new_project,
                                        user=tikedge_user
                                        )
        new_journal_entry.save()

        if len(project_public_status) > 0 and project_public_status:
            new_project.is_public = False
            new_project.save()
            public_status = PondSpecificProject(project=new_project)
            public_status.save()
            if project_public_status == ALL_POND_STATUS:
                for each_pond in user_ponds:
                    public_status.pond.add(each_pond)
                public_status.save()
            else:
                pond = Pond.objects.get(id=int(project_public_status))
                public_status.pond.add(pond)
                public_status.save()
        """
        project_picture = request.POST.get("projectpic")
        if len(project_picture) > 0:
            picture_file = get_picture_from_base64(project_picture)
            if not picture_file:
                response['status'] = False
                response["error"] = "Hey visual must be either jpg, jpeg or png file!"
                return HttpResponse(json.dumps(response), status=201)
            else:
                modules.add_file_to_project_pic(picture_file, new_project)
        new_progress_set = ProgressPictureSet(project=new_project)
        new_progress_set.save()
        """
        new_vid_progress_set = ProgressVideoSet(project=new_project)
        new_vid_progress_set.save()
        new_vouch = VoucheProject(tasks=new_project)
        new_vouch.save()
        new_follow = Follow(tasks=new_project)
        new_follow.save()
        new_seen = SeenProject(tasks=new_project)
        new_seen.save()
        new_goal_or_progress_added_notification_to_pond(new_project, is_new_project=True)
        response["status"] = True

        project_vid = request.POST.get('projectvid')
        if len(project_vid) > 0:
            print(project_vid, " video path")
            #dec_video_file = get_video_from_base64(project_vid)
            video_mod = ProjectVideo(last_edited=timezone.now, project=new_project)
            video_mod.save()
            dec_video_name = upload_video_file(project_vid, video_mod)
            video_mod.video_name = dec_video_name
            video_mod.save()
        return HttpResponse(json.dumps(response), status=201)


class ApiProjectEditView(CSRFExemptView):

    def get(self, request):
        response = {}
        try:
            username = request.GET.get("username")
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            response["status"] = False
            response["error"] = "Log Back In! Try Again!"
            return HttpResponse(json.dumps(response), status=201)
        tikedge_user = TikedgeUser.objects.get(user=user)
        projects = UserProject.objects.filter(user=tikedge_user, is_deleted=False).order_by('-created')
        print "projects", projects
        project_list = []

        timezone = request.GET.get('timezone')
        for each_proj in projects:
            tag_list = []
            for item in each_proj.tags.all():
                tag_list.append(item.name_of_tag)
            project_pic = modules.get_project_pic_info(each_proj)
            project_list.append({
                'proj_name':each_proj.name_of_project,
                'id':each_proj.id,
                'hidden':False,
                'tag_list':tag_list,
                'time':modules.utc_to_local(each_proj.length_of_project, local_timezone=timezone).strftime("%B %d %Y %I:%M %p"),
                'proj_pic_id': project_pic['pic_id'],
                'proj_pic_url': project_pic['url'],
                'has_pic':project_pic['has_pic']

            })
        response["status"] = True
        response["project_list"] = project_list
        return HttpResponse(json.dumps(response), status=201)

    def post(self, request):
        response = {}
        try:
            username = request.POST.get("username")
            User.objects.get(username=username)
        except ObjectDoesNotExist:
            response["status"] = False
            response["error"] = "Log Back In! Try Again!"
            return HttpResponse(json.dumps(response), status=201)
        response = { "status":True }
        if 'update_project' in request.POST:
            mil_id = request.POST.get("update_project")
            tags_obj = request.POST.get("tags")
            tags = tags_obj.split(",")
            proj_id_name = "the_message"
            project_name = request.POST.get(proj_id_name)
            project = UserProject.objects.get(id=int(mil_id))
            project.name_of_project = project_name
            project.last_update = datetime.now()
            for item in project.tags.all():
                project.tags.remove(item)
                project.save()
            try:
                if tags_obj:
                    for item in tags:
                        try:
                            item_obj = TagNames.objects.get(name_of_tag=item)
                        except ObjectDoesNotExist:
                            item_obj = TagNames(name_of_tag=item)
                            item_obj.save()
                        project.tags.add(item_obj)
                    project.save()
            except ValueError:
                pass
        if 'proj_id' in request.POST:
            proj_id = request.POST.get("proj_id")
            project = UserProject.objects.get(id=int(proj_id))
            project.is_deleted = True
            journal = JournalPost.objects.get(new_project_entry=project)
            journal.is_deleted = True
            journal.save()
            if (not project.is_completed) and project.made_live:
                mark_progress_as_deleted(project)
                '''
                for each_proj in project.milestone_set.filter(is_deleted=False, is_active=True):
                    create_failed_notification(each_proj)
                    each_proj.is_live = False
                    each_proj.save()
                '''
                project.save()
            create_failed_notification_proj_by_deletion(project)
            response = {"status":True}
        if 'delete_pic_id' in request.POST:
            pic_id = request.POST.get("delete_pic_id")
            modules.delete_project_picture(pic_id)
            response = {"status":True}
        return HttpResponse(json.dumps(response))


class ApiSendResetPasswordCode(CSRFExemptView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = True
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            activation_code = modules.generate_reset_code(user)
        except ObjectDoesNotExist:
            response['status'] = False
            response['error'] = "Sorry your email does not match an active user!"
            return HttpResponse(json.dumps(response))
        try:
            send_templated_mail(
                template_name='password_reset',
                from_email='pondeye@textdoar.com',
                recipient_list=['pondeye@textdoar.com', user.email],
                context={
                    'reset_code': activation_code,
                     'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                },
                bcc=[CUSTOMER_SERVICE_EMAIL],
                headers={'My-Custom-Header':'Pondeye Team'},
            )
        except (ValueError, AttributeError):
            response['status'] = False
        return HttpResponse(json.dumps(response), status=201)


class ApiPasswordResetView(CSRFExemptView):
    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = True
        try:
            email = request.POST.get("email")
            print "email of users ", email
            user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            response["status"] = False
            response["error"] = "Email is not valid!"
            return HttpResponse(json.dumps(response), status=201)
        token = request.POST.get('token')
        reset = modules.reset_forget_password(user, token)
        if reset:
            new_password = request.POST.get("password")
            user.set_password(new_password)
            user.save()
            response['username'] = user.username
        else:
            response["status"] = False
            response["error"] = "Token not valid!"
        return HttpResponse(json.dumps(response), status=201)


class ApiMilestoneEditView(CSRFExemptView):

    def get(self, request, *args, **kwargs):
        response = {}
        try:
            username = request.GET.get("username")
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            response["status"] = False
            response["error"] = "Log Back In! Try Again!"
            return HttpResponse(json.dumps(response), status=201)
        tikedge_user = TikedgeUser.objects.get(user=user)
        milestones = Milestone.objects.filter(user=tikedge_user, is_deleted=False)
        milestones_list = []
        timezone = request.GET.get('timezone')
        for each_mil in milestones:
            milestones_list.append({
                'mil_name':each_mil.name_of_milestone,
                'id':each_mil.id,
                'time':modules.utc_to_local(each_mil.done_by, local_timezone=timezone).strftime("%B %d %Y %I:%M %p"),
                'hidden': False
            })
        response["status"] = True
        response["milestones_list"] = milestones_list
        if milestones_list:
            response['hasMilestone'] = True
        else:
            response['hasMilestone'] = False
        return HttpResponse(json.dumps(response), status=201)

    def post(self, request, *args, **kwargs):
        response = {"status": False}
        response["error"] = "No update action was taken!"
        if 'update_milestone' in request.POST:
            mil_id = request.POST.get("update_milestone")
            mil_id_name = "updated_name"
            milestone_name = request.POST.get(mil_id_name)
            milestone = Milestone.objects.get(id=int(mil_id))
            milestone.name_of_milestone = milestone_name
            milestone.last_update = datetime.now()
            milestone.save()
            response = { "status":True }
        if 'delete_milestone' in request.POST:
            mil_id = request.POST.get("delete_milestone")
            milestone = Milestone.objects.get(id=int(mil_id))
            milestone.is_deleted = True
            try:
                journal = JournalPost.objects.get(milestone_entry=milestone)
                journal.is_deleted = True
                journal.save()
            except ObjectDoesNotExist:
                pass
            if not milestone.is_completed:
                create_failed_notification(milestone)
                milestone.is_active = False
            milestone.save()
            response = {"status":True}
        return HttpResponse(json.dumps(response), status=201)


class ApiChangePersonalInformationView(CSRFExemptView):

    def get(self, request):
        response = {}
        try:
            username = request.GET.get("username")
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            response["status"] = False
            response["error"] = "Log Back In! Try Again!"
            return HttpResponse(json.dumps(response), status=201)
        tikedge_user = TikedgeUser.objects.get(user=user)
        response['first_name'] = tikedge_user.user.first_name,
        response['last_name'] = tikedge_user.user.last_name,
        response['email'] = tikedge_user.user.email
        return HttpResponse(json.dumps(response), status=201)

    def post(self, request):
        response = {}
        try:
            username = request.POST.get("username")
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            response["status"] = False
            response["error"] = "Log Back In! Try Again!"
            return HttpResponse(json.dumps(response), status=201)
        tikedge_user = TikedgeUser.objects.get(user=user)
        if 'save_changes' in request.POST:
            tikedge_user.user.first_name = request.POST.get('first_name')
            tikedge_user.user.last_name = request.POST.get('last_name')
            tikedge_user.user.email = request.POST.get('email')
            tikedge_user.user.save()
            tikedge_user.save()
        if 'save_password' in request.POST:
            new_password = request.POST.get("password")
            old_password = request.POST.get("old_password")
            print "tikedge user edit first name ", request.POST.get('password') , " ", request.POST.get("old_password")
            if authenticate(username=user.username, password=old_password):
                user.set_password(new_password)
                user.save()
            else:
                response["status"] = False
                response["error"] = "Original Password is Invalid!"
                return HttpResponse(json.dumps(response), status=201)
            response["status"] = True
        return HttpResponse(json.dumps(response), status=201)


class ApiProfileView(CSRFExemptView):

    def get(self, request):
        response = {}
        try:
            username = request.GET.get("username")
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            response["status"] = False
            response["error"] = "Log Back In! Try Again!"
            return HttpResponse(json.dumps(response), status=201)
        other_user_id = request.GET.get("other_user_id")
        try:
            other_user = User.objects.get(id=int(other_user_id))
        except ValueError:
            other_user = user
        tikedge_user = TikedgeUser.objects.get(user=other_user)
        requesting_user = TikedgeUser.objects.get(user=user)
        current_proj_dj = get_recent_projects(tikedge_user.user, requesting_user)
        current_projs = get_recent_projects_json(current_proj_dj)
        all_projects_dj = get_recent_projects(tikedge_user.user, requesting_user, is_live=False)
        all_projs = get_recent_projects_json(all_projects_dj)
        current_tasks = get_todays_milestones_json(tikedge_user.user, current_proj_dj)
        profile_url = get_profile_pic_json(tikedge_user)
        try:
            prof_storage = ProfilePictures.objects.get(tikedge_user=tikedge_user).profile_pics.url
        except (ValueError, AttributeError, ObjectDoesNotExist):
            prof_storage = None

        aval_pond = available_ponds_json(tikedge_user, user)
        profile_info = {
            'first_name':tikedge_user.user.first_name,
            'last_name':tikedge_user.user.last_name,
            'user_id':tikedge_user.id,
            'current_tasks':current_tasks,
            'current_projs':current_projs,
            'profile_url': profile_url,
            'profile_url_storage': prof_storage,
            'aval_pond':aval_pond,
            'is_own_profile': user == other_user,
            'user_name':tikedge_user.user.username,
            'all_projects':all_projs,
            'user_stats': modules.user_stats(other_user),
        }
        response['user_details'] = profile_info
        return HttpResponse(json.dumps(response), status=201)


class ApiProfilePictureView(CSRFExemptView):

    def post(self, request):
        response = {}
        try:
            username = request.POST.get("username")
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            response["status"] = False
            response["error"] = "Log Back In! Try Again!"
            return HttpResponse(json.dumps(response), status=201)
        picture = request.POST.get('picture')
        picture_file = get_picture_from_base64(picture)
        if not picture_file:
            response['status'] = False
            response["error"] = "Hey visual must be either jpg, jpeg or png file!"
            return HttpResponse(json.dumps(response), status=201)
        tkduser = TikedgeUser.objects.get(user=user)
        try:
           ProfilePictures.objects.get(tikedge_user=tkduser).delete()
        except ObjectDoesNotExist:
            pass
        picture_file.file = resize_image(picture_file, is_profile_pic=True)
        try:
           picture_mod = ProfilePictures.objects.get(tikedge_user=tkduser)
           picture_mod.profile_pics = picture_file
           picture_mod.image_name = picture_file.name
        except ObjectDoesNotExist:
           picture_mod = ProfilePictures(image_name=picture_file.name, profile_pics=picture_file, tikedge_user=tkduser)
        picture_mod.save()
        tikedge_user = TikedgeUser.objects.get(user=user)
        profile_url = get_profile_pic_json(tikedge_user)
        response = {
           'status':True,
           'url':profile_url
        }
        return HttpResponse(json.dumps(response), status=201)


class ApiCheckMilestoneDone(CSRFExemptView):
    def post(self, request):
        response = {}
        try:
            username = request.POST.get("username")
            User.objects.get(username=username)
        except ObjectDoesNotExist:
            response["status"] = False
            response["error"] = "Log Back In! Try Again!"
            return HttpResponse(json.dumps(response), status=201)
        try:
            mil_stone = Milestone.objects.get(id=int(request.POST.get("mil_id")))
            if not mil_stone.is_failed:
                mil_stone.is_completed = True
                mil_stone.is_active = False
                mil_stone.save()
            response["status"] = True
        except (AttributeError, ValueError, TypeError, ObjectDoesNotExist):
            response["status"] = False
            response["error"] = "Something Went Wrong Try Again!"
        return HttpResponse(json.dumps(response), status=201)


class ApiCheckProjectDone(CSRFExemptView):
    def post(self, request):
        response = {}
        try:
            username = request.POST.get("username")
            User.objects.get(username=username)
        except ObjectDoesNotExist:
            response["status"] = False
            response["error"] = "Log Back In! Try Again!"
            return HttpResponse(json.dumps(response), status=201)
        try:
            proj_stone = UserProject.objects.get(id=int(request.POST.get("proj_id")))
            """
            proj_stone.is_completed = True
            proj_stone.is_live = False
            proj_stone.save()
            """
            progress_set = ProgressVideoSet.objects.get(project=proj_stone)
            begin_timeline_video(progress_set)
            response["status"] = True
        except None:
            # (AttributeError, ValueError, TypeError, ObjectDoesNotExist):
            response["status"] = False
            response["error"] = "Something Went Wrong Try Again!"
        return HttpResponse(json.dumps(response), status=201)


class ApiCheckFailedProjectMilestoneView(CSRFExemptView):

    def post(self, request):
        response = {}
        token = request.POST.get("token")
        if token and (token == TOKEN_FOR_NOTIFICATION):
            response["status"] = True
            confirm_expired_project()
        else:
            response["status"] = False
            response["error"] = "Invalid Token"
            response['token_given'] = token
        return HttpResponse(json.dumps(response), status=201)


class ApiRunRanking(CSRFExemptView):

    def post(self, request):
        response = {}
        token = request.POST.get("token")
        if token and (token == TOKEN_FOR_NOTIFICATION):
            response["status"] = True
            modules.global_ranking_algorithm()
        else:
            response["status"] = False
            response["error"] = "Invalid Token"
            response['token_given'] = token
        return HttpResponse(json.dumps(response), status=201)
