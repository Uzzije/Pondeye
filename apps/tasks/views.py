from django.shortcuts import render
from django.views.generic import View, FormView
from forms import tasks_forms
from models import User, TikedgeUser, Tasks, UserProject
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from datetime import timedelta
from modules import get_user_projects, tasks_search, get_current_todo_list, get_todays_todo_list, is_time_conflict, \
    convert_html_to_datetime, time_has_past, get_current_todo_list_json_form, get_todays_todo_list_json
from django_bootstrap_calendar.models import CalendarEvent
from actstream import action
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from datetime import datetime
from serializer import UserAuthenticationSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json


class RegisterView(View):

    def get(self, request):
        form = tasks_forms.RegisterForm()
        return render(request, 'tasks/register.html', {'form':form})

    def post(self, request):
        form = tasks_forms.RegisterForm(request.POST)
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
            return render(request, 'tasks/register.html', {'form': form})


class HomeView(View):

    def get(self, request):
        if not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('tasks:login'))
        current_task = get_current_todo_list(request.user)
        todays_to_do_list = get_todays_todo_list(request.user)
        return render(request, 'tasks/home.html', {'current_task':current_task, 'todays_tasks':todays_to_do_list})


class ListOfTasksViews(View):

    def get(self, request):
        result = None
        if 'get_tasks' in request.GET and request.GET['get_tasks']:
            query_string = str(request.GET['get_tasks'])
            result = tasks_search(query_string, request.user)
            return render(request, 'tasks/list_of_tasks.html', {'results':result})
        return render(request, 'tasks/list_of_tasks.html', {'results':result})


class LoginView(FormView):

    form_class = tasks_forms.LoginForm
    template_name = 'tasks/login.html'

    def get_success_url(self):
        tikedge_user = TikedgeUser.objects.get(user=self.request.user)
        tikedge_user.save()
        return reverse('tasks:home')

    def form_valid(self, form):
        name = form.cleaned_data.get('name')
        password = form.cleaned_data.get('password')
        user = authenticate(username=name, password=password)
        if not user.is_active:
            user.is_active = True
            user.save()
        login(self.request, user)
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        """Use this to add extra context."""
        context = super(LoginView, self).get_context_data(**kwargs)
        try:
            context['user_name'] = self.request.user.username
        except (None, TypeError, KeyError):
            context['user_name'] = "guest"
        return context


class ApiLoginView(View):

    def get(self, request,  *args, **kwargs):
        response_data ={}
        name = request.GET.get('username')
        password = request.GET.get('password')
        user = authenticate(username=name, password=password)
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


class CSRFExemptView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CSRFExemptView, self).dispatch(*args, **kwargs)


class CSRFEnsureCookiesView(View):
    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super(CSRFEnsureCookiesView, self).dispatch(*args, **kwargs)


class ApiStartUserSession(CSRFExemptView):

    def get(self, request,  *args, **kwargs):
        username = request.GET.get("username")
        password = request.GET.get("password")
        response_data = {}
        try:
            user = User.objects.get(username=username)
            print "should authenticate"
        except ObjectDoesNotExist:
            print "not authenticated , ", username
            user = None
        users = authenticate(username=username, password=password)
        if users:
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            user.save()
            login(request, user)
            response_data['authenticate'] = "true"
        else:
            print password
            response_data['authenticate'] = "false"
        return HttpResponse(json.dumps(response_data), status=201)


class ApiRegistrationView(CSRFEnsureCookiesView):

    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
         user_name = request.POST.get('user_name')
         password = request.POST.get('password')
         email = request.POST.get('email')
         first_name = request.POST.get('first_name')
         last_name = request.POST.get('last_name')
         response_data = {}
         response_data['success'] = "Name is not valid!"
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


class AddTasks(View):

    def get(self, request):
        if not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('tasks:login'))
        form = tasks_forms.AddTaskForm(user=request.user)
        return render(request, 'tasks/add_tasks.html', {'form':form, 'existing_project':get_user_projects(request.user)})

    def post(self, request):
        form = tasks_forms.AddTaskForm(user=request.user, data=request.POST)
        user = TikedgeUser.objects.get(user=request.user)
        if form.is_valid():
            name_of_task = form.cleaned_data['to_do_item']
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']
            new_project = form.cleaned_data['new_project']
            existing_project = request.POST.get('existing_project')
            tasks = Tasks(name_of_tasks=name_of_task, user=user)
            tasks.save()
            if start_time:
                if is_time_conflict(request.user, start_time, end_time):
                    msg = "Hey, one tasks at a time"
                    form.add_error('start_time', msg)
                    return render(request, 'tasks/add_tasks.html', {'form':form, 'existing_project':get_user_projects(request.user)})
                tasks.start = start_time
                tasks.save()
                if end_time:
                    tasks.end = start_time + timedelta(minutes=int(end_time))
                else:
                    tasks.end = start_time + timedelta(minutes=60)
                tasks.is_active = True
                tasks.save()
                new_calender_event = CalendarEvent(title=name_of_task, start=start_time, end=tasks.end, css_class='event-info')
                new_calender_event.save()
                action.send(user, verb='Created A to do list item: ', target=tasks)
            if new_project:
                if not user.userproject_set.all().filter(name_of_project=new_project):
                    project = UserProject(name_of_project=new_project, user=user)
                    project.save()
                    tasks.project = project
                    tasks.part_of_project = True
                    tasks.save()
            if existing_project:
                project = user.userproject_set.all().get(name_of_project=existing_project)
                project.save()
                tasks.project = project
                tasks.part_of_project = True
                tasks.save()
            return HttpResponseRedirect(reverse('tasks:home'))
        return render(request, 'tasks/add_tasks.html', {'form':form, 'existing_project':get_user_projects(request.user)})


class ApiTaskView(CSRFExemptView):

    def get(self, request, *args, **kwargs):
        response = {}
        try:
            username = request.GET.get('username')
            user_obj = User.objects.get(username=username)
        except ObjectDoesNotExist:
            response['status'] = "false"
            return HttpResponse(json.dumps(response), status=201)
        what_to_get = request.GET.get("get_what")
        if what_to_get == "tasks_info":
            current_task = get_current_todo_list_json_form(user_obj)
            todays_to_do_list = get_todays_todo_list_json(user_obj)
            print todays_to_do_list
            response['upcoming_task'] = current_task
            response['tasks'] = todays_to_do_list
            response['status'] = "true"
        else:
            project = get_user_projects(user_obj)
            response['users_project'] = project
            response['status'] = "true"
        return HttpResponse(json.dumps(response), status=201)

    def post(self, request, *args, **kwargs):
        response_data = {}
        user_name = request.POST.get('username')
        user_obj = User.objects.get(username=user_name)
        user = TikedgeUser.objects.get(user=user_obj)
        name_of_task = request.POST.get('to_do_item')
        end_time = request.POST.get('end_time')
        try:
            start_time_r = convert_html_to_datetime(request.POST.get('start_time'))
            start_time = datetime.strptime(start_time_r, '%Y-%m-%d %H:%M')
            print start_time
        except (ValueError, IndexError):
            start_time = None
        new_project = request.POST.get('new_project')
        existing_project = request.POST.get('existing_project')
        tasks = Tasks(name_of_tasks=name_of_task, user=user)
        tasks.save()
        if start_time:
            print end_time
            msg = time_has_past(start_time)
            if msg:
                response_data['success'] = msg
                return HttpResponse(json.dumps(response_data), status=201)
            if is_time_conflict(user_obj, start_time, end_time):
                msg = "Hey, one tasks at a time"
                response_data['success'] = msg
                return HttpResponse(json.dumps(response_data), status=201)
            tasks.start = start_time
            tasks.save()
            if end_time:
                tasks.end = start_time + timedelta(minutes=int(end_time))
            else:
                tasks.end = start_time + timedelta(minutes=60)
            tasks.is_active = True
            tasks.save()
            new_calender_event = CalendarEvent(title=name_of_task, start=start_time, end=tasks.end, css_class='event-info')
            new_calender_event.save()
        if new_project:
            if not user.userproject_set.all().filter(name_of_project=new_project):
                project = UserProject(name_of_project=new_project, user=user)
                project.save()
                tasks.project = project
                tasks.part_of_project = True
                tasks.save()
        if existing_project and not new_project:
            print existing_project
            project = user.userproject_set.all().get(name_of_project=existing_project)
            project.save()
            tasks.project = project
            tasks.part_of_project = True
            tasks.save()
        response_data['success'] = "true"
        return HttpResponse(json.dumps(response_data), status=201)


class LogoutView(View):

    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('tasks:login'))