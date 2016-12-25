from django.shortcuts import render
from django.views.generic import View, FormView
from forms import tasks_forms
from models import User, TikedgeUser, UserProject,Milestone, TagNames, LaunchEmail
from ..social.models import ProfilePictures, JournalPost
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from datetime import timedelta
from ..social.modules import get_journal_message, \
    get_notifications, get_pond, resize_image, available_ponds
from modules import get_user_projects, \
    time_has_past,\
    get_todays_milestones, \
    confirm_expired_milestone_and_project, get_completed_mil_count, get_completed_proj_count, get_failed_mil_count, \
    get_failed_proj_count, get_recent_projects, get_status, display_error
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from datetime import datetime
from ..social.global_variables import MILESTONE, NEW_PROJECT
from friendship.models import Friend
import json
from django.contrib import messages
from braces.views import LoginRequiredMixin
from global_variables_tasks import TAG_NAMES_LISTS
from .forms import launch_form


class RegisterView(View):

    def get(self, request):
        form = tasks_forms.RegisterForm()
        return render(request, 'tasks/register.html', {'form':form})

    def post(self, request):
        form = tasks_forms.RegisterForm(request.POST)
        print "hitting here"
        if form.is_valid():
            user_name = form.cleaned_data.get('user_name')
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            user = User.objects.create_user(username=user_name, password=password, email=email, first_name=first_name,
                                            last_name=last_name)
            user.save()
            tickedge_user = TikedgeUser(user=user)
            tickedge_user.save()
            self.request.session['user_name'] = user_name
            self.request.session['email'] = email
            self.request.session['first_name'] = tickedge_user.user.first_name
            return HttpResponseRedirect(reverse('tasks:home'))
        else:
            display_error(form, request)
            return render(request, 'tasks/register.html', {'form': form})


class PreLaunchView(View):

    def get(self, request):
        form = launch_form.LaunchForm()
        return render(request, 'base/pre-launch.html', {'form':form})

    def post(self, request):
        form = launch_form.LaunchForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            try:
                LaunchEmail.objects.get(email=email)
                messages.info(request, "Hey! You are already registered!")
                return render(request, 'base/pre-launch.html', {'form':form})
            except ObjectDoesNotExist:
                new_email = LaunchEmail(email=email)
                new_email.save()
                messages.success(request, "Thanks! We will let you know when we go live!")
                return render(request, 'base/pre-launch.html', {'form':form})
        display_error(form, request)
        return render(request, 'base/pre-launch.html', {'form':form})


class HomeView(LoginRequiredMixin, View):

    def get(self, request):
        if not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('tasks:login'))
        current_task = get_todays_milestones(request.user)
        current_projs = get_recent_projects(request.user)
        failed_mil_count = get_failed_mil_count(request.user)
        completed_mil_count = get_completed_mil_count(request.user)
        failed_proj_count = get_failed_proj_count(request.user)
        completed_proj_count = get_completed_proj_count(request.user)
        tikedge_user = TikedgeUser.objects.get(user=request.user)
        notifications = get_notifications(request.user)
        status_of_user = get_status(request.user)
        try:
            has_prof_pic = ProfilePictures.objects.get(tikedge_user=tikedge_user)
        except ObjectDoesNotExist:
            has_prof_pic = None
            pass
        user_picture_form = tasks_forms.PictureUploadForm()
        ponders = get_pond(request.user)[0:5]
        return render(request, 'tasks/home.html', {'current_tasks':current_task,
                                                   'failed_mil_count':failed_mil_count, 'has_prof_pic':has_prof_pic,
                                                   'user_picture_form':user_picture_form,
                                                   'notifications':notifications,
                                                   'user_name':request.user.username,
                                                   'ponders': ponders, 'completed_mil_count':completed_mil_count,
                                                   'failed_proj_count':failed_proj_count,
                                                   'complete_proj_count':completed_proj_count,
                                                    'current_projs':current_projs,
                                                    'status_of_user':status_of_user,
                                                    'tikedge_user':tikedge_user
                                                   })

    def post(self, request):
        user_picture_form = tasks_forms.PictureUploadForm(request.POST, request.FILES)
        if user_picture_form.is_valid():
            tkduser = TikedgeUser.objects.get(user=request.user)
            picture_file = request.FILES.get('picture', False)
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
            current_task = get_todays_milestones(request.user)
            current_projs = get_recent_projects(request.user)
            failed_mil_count = get_failed_mil_count(request.user)
            completed_mil_count = get_completed_mil_count(request.user)
            failed_proj_count = get_failed_proj_count(request.user)
            completed_proj_count = get_completed_proj_count(request.user)
            tikedge_user = TikedgeUser.objects.get(user=request.user)
            notifications = get_notifications(request.user)
            status_of_user = get_status(request.user)
            try:
                has_prof_pic = ProfilePictures.objects.get(tikedge_user=tikedge_user)
            except ObjectDoesNotExist:
                has_prof_pic = None
                pass
            user_picture_form = tasks_forms.PictureUploadForm()
            ponders = get_pond(request.user)
            return render(request, 'tasks/home.html', {'current_tasks':current_task,
                                                       'failed_mil_count':failed_mil_count, 'has_prof_pic':has_prof_pic,
                                                       'user_picture_form':user_picture_form,
                                                       'notifications':notifications,
                                                       'user_name':request.user.username,
                                                       'ponders': ponders, 'completed_mil_count':completed_mil_count,
                                                       'failed_proj_count':failed_proj_count,
                                                       'complete_proj_count':completed_proj_count,
                                                        'current_projs':current_projs,
                                                        'status_of_user':status_of_user,
                                                        'tikedge_user':tikedge_user
                                                       })
        print "something went wrong"

        return HttpResponse(request, 'tasks/home.html', {'user_picture_form':user_picture_form})


class ProfileView(LoginRequiredMixin, View):

    def get(self, request, user_name):
        if not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('tasks:login'))
        user = User.objects.get(username=user_name)
        current_tasks = get_todays_milestones(user)
        current_projs = get_recent_projects(user)
        tikedge_user = TikedgeUser.objects.get(user=user)
        failed_mil_count = get_failed_mil_count(user)
        completed_mil_count = get_completed_mil_count(user)
        failed_proj_count = get_failed_proj_count(user)
        completed_proj_count = get_completed_proj_count(user)
        status_of_user = get_status(user)
        print " friend request ", Friend.objects.unrejected_requests(user=request.user)
        try:
            has_prof_pic = ProfilePictures.objects.get(tikedge_user=tikedge_user)
        except ObjectDoesNotExist:
            has_prof_pic = None
        user_picture_form = tasks_forms.PictureUploadForm()
        aval_pond = available_ponds(tikedge_user, request.user)
        return render(request, 'tasks/profile_view.html', {'current_tasks':current_tasks,
                                                    'has_prof_pic':has_prof_pic,
                                                   'user_picture_form':user_picture_form,'user':tikedge_user,
                                                    'completed_mil_count':completed_mil_count,
                                                   'failed_proj_count':failed_proj_count,
                                                   'complete_proj_count':completed_proj_count,
                                                    'failed_mil_count':failed_mil_count,
                                                    'current_projs':current_projs,
                                                    'status_of_user':status_of_user,
                                                    "user_name":user.username,
                                                    "aval_pond":aval_pond
                                                   })


class LoginView(FormView):

    form_class = tasks_forms.LoginForm
    template_name = 'tasks/login.html'

    def get_success_url(self):
        try:
            url_with_next = self.request.POST.get('next', "")
            if url_with_next == "":
                return reverse('tasks:todo_feed')
            return url_with_next
        except:
            pass
        return reverse('social:todo_feed')

    def form_valid(self, form):
        name = form.cleaned_data.get('name')
        password = form.cleaned_data.get('password')
        user = authenticate(username=name, password=password)
        if not user.is_active:
            user.is_active = True
            user.save()
        login(self.request, user)
        return super(LoginView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        """Use this to add extra context."""
        context = super(LoginView, self).get_context_data(**kwargs)
        try:
            context['user_name'] = self.request.user.username
        except (None, TypeError, KeyError):
            context['user_name'] = "guest"
        return context


class CSRFExemptView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CSRFExemptView, self).dispatch(*args, **kwargs)


class CSRFEnsureCookiesView(View):
    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super(CSRFEnsureCookiesView, self).dispatch(*args, **kwargs)


class AddProject(LoginRequiredMixin, View):

    def get(self, request):
        if not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('tasks:login'))
        form = tasks_forms.AddTaskForm(user=request.user)
        proj_form = tasks_forms.AddProjectForm()
        mil_form = tasks_forms.AddMilestoneForm()
        tag_names = TagNames.objects.all()
        return render(request, 'tasks/add_view.html', {'form':form,'tag_names':TAG_NAMES_LISTS,
                                                       'existing_project':get_user_projects(request.user),
                                                       'proj_form': proj_form,
                                                       'mil_form': mil_form
                                                       })

    def post(self, request):
        user = TikedgeUser.objects.get(user=request.user)
        tag_names = TagNames.objects.all()
        proj_form = tasks_forms.AddProjectForm(request.POST)
        mil_form = tasks_forms.AddMilestoneForm(request.POST)

        if 'mil_create' in request.POST:
            print "Making a new milestone"
            name_of_milestone = request.POST.get('milestone_name')
            if len(name_of_milestone) > 600:
                messages.error(request, "Way too much words!")
                return render(request, 'tasks/add_view.html', {'tag_names':tag_names,
                                                       'existing_project':get_user_projects(request.user),
                                                        'proj_form': proj_form,
                                                       'mil_form': mil_form})
            name_of_project = request.POST.get('name_of_mil_proj')
            try:
                #done_by_r = convert_html_to_datetime(request.POST.get('done_by_mil'))
                if mil_form.is_valid():
                    done_by = mil_form.cleaned_data.get('milestone_date')
                    print "done is time ", done_by
                else:
                    done_by = None
                    print "legit one done by", done_by
            except (ValueError, IndexError):
                done_by = None
                messages.error(request, "Your date input seems to be wrong!")
            length_of_time = request.POST.get('length_of_time')
            print "this is length of time ", length_of_time
            user_project = UserProject.objects.get(name_of_project=name_of_project, user=user)
            if (name_of_milestone != '') and done_by and (name_of_project != '') and (done_by != '') \
                    and (not time_has_past(done_by)):
                print "time has not passed! ", done_by
                if (length_of_time != '') and (length_of_time != '-1'):
                    start_time = done_by - timedelta(hours=int(length_of_time))
                else:
                    if length_of_time == '-1':
                        start_time = done_by - timedelta(minutes=5)
                        print "in here for no time", "done by ", done_by, "and start time: ", start_time
                    else:
                        start_time = done_by - timedelta(minutes=57)
                print "done by ",done_by, "and start time: ", start_time
                if not time_has_past(start_time) and user_project.length_of_project >= start_time and \
                        user_project.length_of_project >= done_by:
                    new_milestone = Milestone(name_of_milestone=name_of_milestone, user=user, reminder=start_time,
                                          done_by=done_by, project=user_project)
                    new_milestone.save()
                    day_entry = user.journalpost_set.all().count()
                    new_journal_entry = JournalPost(entry_blurb=get_journal_message(MILESTONE,
                                                                                    milestone=new_milestone.blurb,
                                                                                    project=user_project.blurb),
                                                                                    day_entry=day_entry + 1,
                                                                                    event_type=MILESTONE,
                                                                                    is_milestone_entry=True,
                                                                                    milestone_entry=new_milestone,
                                                                                    user=user,
                                                                                 )
                    new_journal_entry.save()
                    messages.success(request, "Successfully added a Milestone to %s project" % name_of_project)
                    return HttpResponseRedirect(reverse('tasks:home'))
                elif time_has_past(start_time):
                    messages.error(request, "Hey, not enough time to complete milestone! Milestone must take at least 5 minutes!")
                elif user_project.length_of_project >= start_time:
                    messages.error(request, "Hey, can't fit this milestone into the project scope, takes too long!")
                else:
                    print "print buisiness ",user_project.length_of_project, done_by
                    messages.error(request, "Hey, can't fit this milestone into the project scope!")
            else:
                messages.error(request, "Hey, there might be a time conflict!")
        if 'proj_create' in request.POST or 'proj_save' in request.POST:
            try:
                if proj_form.is_valid():
                    end_by = proj_form.cleaned_data.get('project_date')
                else:
                    end_by = None
                    print end_by, "legit one end by"
            except (ValueError, IndexError):
                messages.error(request, "It seems like your date input is wrong!")
                return render(request, 'tasks/add_view.html', {'tag_names':TAG_NAMES_LISTS,
                                                       'existing_project':get_user_projects(request.user),
                                                       'proj_form': proj_form,
                                                       'mil_form': mil_form})
            if not time_has_past(end_by):
                name_of_project = request.POST.get('name_of_project')
                tags = request.POST.getlist('tags')
                print tags
                new_project = UserProject(name_of_project=name_of_project, user=user, length_of_project=end_by)
                new_project.save()
                if 'proj_create' in request.POST:
                    new_project.is_live = True
                    new_project.made_live = datetime.now()
                    messages.success(request, "Sweet! %s has begun!" % name_of_project)
                else:
                    messages.success(request, "Sweet! %s has been created!" % name_of_project)
                for item in tags:
                    print tags, " tags why"
                    try:
                        item_obj = TagNames.objects.get(name_of_tag=item)
                    except ObjectDoesNotExist:
                        item_obj = TagNames(name_of_tag=item)
                        item_obj.save()
                    new_project.tags.add(item_obj)
                new_project.save()
                day_entry = user.journalpost_set.all().count()
                new_journal_entry = JournalPost(
                                                entry_blurb=get_journal_message(NEW_PROJECT, project=new_project.blurb),
                                                day_entry=day_entry + 1,
                                                event_type=NEW_PROJECT,
                                                is_project_entry=True,
                                                new_project_entry=new_project,
                                                user=user
                                                )
                new_journal_entry.save()
                return HttpResponseRedirect(reverse('tasks:home'))
            else:
                messages.error(request, "There seems to be a time conflict")
        #messages.error(request, "Dude something went wrong! Try again.")
        return render(request, 'tasks/add_view.html', {'tag_names':tag_names,
                                                       'existing_project':get_user_projects(request.user),
                                                       'proj_form': proj_form,
                                                       'mil_form': mil_form
                                                       })


class LogoutView(View):

    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('tasks:login'))


class CheckMilestoneDone(View):
    def post(self, request):
        response = {}
        mil_stone = Milestone.objects.get(id=int(request.POST.get("mil_Id")))
        if not mil_stone.is_failed:
            mil_stone.is_completed = True
            mil_stone.is_active = False
            mil_stone.save()
        response["status"] = True
        return HttpResponse(json.dumps(response), status=201)


class CheckPojectDone(View):
    def post(self, request):
        response = {}
        try:
            proj_stone = UserProject.objects.get(id=int(request.POST.get("proj_id")))
            proj_stone.is_completed = True
            proj_stone.is_live = False
            proj_stone.save()
            response["status"] = True
            all_milestones = proj_stone.milestone_set.all()
            for each_mil in all_milestones:
                each_mil.is_active = False
                if not each_mil.is_failed:
                    each_mil.is_completed = True
                each_mil.save()
        except (AttributeError, ValueError, TypeError, ObjectDoesNotExist):
            response["status"] = False
        return HttpResponse(json.dumps(response), status=201)


class CheckFailedProjectMilestoneView(View):

    def post(self, request):
        response = {}
        try:
            tikedge_user = TikedgeUser.objects.get(user=request.user)
            confirm_expired_milestone_and_project(tikedge_user)
            response["status"] = True
        except ObjectDoesNotExist:
            response["status"] = False
        return HttpResponse(json.dumps(response), status=201)



