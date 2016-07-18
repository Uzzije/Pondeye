from django.shortcuts import render
from django.views.generic import View, FormView
from forms import tasks_forms
from models import User, TikedgeUser, Tasks, UserProject
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login
from datetime import timedelta
from modules import get_user_projects, tasks_search, get_current_todo_list, get_todays_todo_list, is_time_conflict
from django_bootstrap_calendar.models import CalendarEvent
from actstream import action


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
                    tasks.save()
            if existing_project:
                project = user.userproject_set.all().get(name_of_project=existing_project)
                project.save()
                tasks.project = project
                tasks.save()
            return HttpResponseRedirect(reverse('tasks:home'))
        return render(request, 'tasks/add_tasks.html', {'form':form, 'existing_project':get_user_projects(request.user)})
