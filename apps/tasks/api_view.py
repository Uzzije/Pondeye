from django.shortcuts import render
from django.views.generic import View, FormView
from forms import tasks_forms
from models import User, TikedgeUser, UserProject,Milestone, TagNames, LaunchEmail
from ..social.models import ProfilePictures, JournalPost, PondSpecificProject, Pond
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from datetime import timedelta
from ..social.modules import get_journal_message, \
    get_notifications_alert, get_pond, resize_image, available_ponds, create_failed_notification, create_failed_notification_proj
from modules import get_user_projects, \
    time_has_past, convert_html_to_datetime,\
    get_todays_milestones, \
    confirm_expired_milestone_and_project, get_completed_mil_count, get_completed_proj_count, get_failed_mil_count, \
    get_failed_proj_count, get_recent_projects, get_status, display_error, api_get_user_projects
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from datetime import datetime
from ..social.global_variables import MILESTONE, NEW_PROJECT, ALL_POND_STATUS
from friendship.models import Friend
import json
from django.contrib import messages
from braces.views import LoginRequiredMixin
from global_variables_tasks import TAG_NAMES_LISTS
from .forms import launch_form
import modules
from forms.form_module import get_current_datetime
from django.db.models import Q
import pytz
from tzlocal import get_localzone


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
            response_data['success'] = "true"
            login(self.request, user)
        else:
            response_data['success'] = "false"
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
        done_by = convert_html_to_datetime(request.POST.get('milestone_date'))
        if done_by:
            if time_has_past(done_by):
                response["status"] = False
                response["error"] = "The time for milestone completion has past!"
                return HttpResponse(json.dumps(response), status=201)
        else:
            response["status"] = False
            response["error"] = "Your date input seems to be wrong!"
            return HttpResponse(json.dumps(response), status=201)
        user_project = UserProject.objects.get(id=name_of_project, user=tikedge_user)
        if len(length_of_time) != 0 and length_of_time != '-1':
                start_time = done_by - timedelta(hours=int(length_of_time))
                if time_has_past(start_time):
                    response["status"] = False
                    response["error"] = "The time for milestone completion has past!"
                    return HttpResponse(json.dumps(response), status=201)
        else:
            start_time = done_by - timedelta(minutes=20)
            if time_has_past(start_time):
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
        response["status"] = True
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
        if conver_date:
            end_by = convert_html_to_datetime(conver_date)
        else:
            response["status"] = False
            response["error"] = "It seems like your date input is wrong!"
            return HttpResponse(json.dumps(response), status=201)
        if time_has_past(end_by):
            response["status"] = False
            response["error"] = "It seems like your date input is in the past!"
            return HttpResponse(json.dumps(response), status=201)
        tikedge_user = TikedgeUser.objects.get(user=user)
        new_project = UserProject(name_of_project=name_of_project, is_live=True,
                                  made_live=datetime.now(), user=tikedge_user, length_of_project=end_by)
        new_project.save()
        for item in tags:
            try:
                item_obj = TagNames.objects.get(name_of_tag=item)
            except ObjectDoesNotExist:
                item_obj = TagNames(name_of_tag=item)
                item_obj.save()
            new_project.tags.add(item_obj)
        new_project.save()
        day_entry = tikedge_user.journalpost_set.all().count()
        new_journal_entry = JournalPost(
                                        entry_blurb=get_journal_message(NEW_PROJECT, project=new_project.blurb),
                                        day_entry=day_entry + 1,
                                        event_type=NEW_PROJECT,
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
        response["status"] = True
        return HttpResponse(json.dumps(response), status=201)

