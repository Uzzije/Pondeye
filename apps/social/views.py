from django.shortcuts import render
from django.views.generic import View
from forms import social_forms
from models import ProfilePictures, Notification
from ..tasks.models import TikedgeUser, UserProject, User
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from encouragements_list import FAIL
from django.core.exceptions import ObjectDoesNotExist
import modules
from friendship.models import Friend
from tasks_feed import NotificationFeed
# Create your views here.


class ProfileView(View):

    def get(self, request):
        activities = modules.get_user_activities(request.user)
        user_picture_form = social_forms.PictureUploadForm()
        tkdge = TikedgeUser.objects.get(user=request.user)
        try:
            user_pic = ProfilePictures.objects.get(tikede_user=tkdge)
        except ObjectDoesNotExist:
            user_pic = None
        try:
            projects = UserProject.objects.filter(user=tkdge)
        except ObjectDoesNotExist:
            projects = None
        word_of_ecouragement = FAIL
        return render(request, 'social/profile.html', {'user_pic':user_pic, 'projects':projects,
                                                       'user_picture_form':user_picture_form, 'activities':activities})


class PictureUploadView(View):

    def get(self, request):
        user_picture_form = social_forms.PictureUploadForm()
        return render(request, 'social/picture_upload.html', {'user_picture_form':user_picture_form})

    def post(self, request):
        user_picture_form = social_forms.PictureUploadForm(request.POST, request.FILES)
        if user_picture_form.is_valid():
            tkduser = TikedgeUser.objects.get(user=request.user)
            picture_file = request.FILES.get('picture', False)
            picture_mod = ProfilePictures(image_name=picture_file.name, profile_pics=picture_file, tikede_user=tkduser)
            picture_mod.save()

            return HttpResponseRedirect(reverse('social:profile_view'))
        return render(request, 'social/picture_upload.html', {'user_picture_form':user_picture_form})


class HomeActivityView(View):

    def get(self, request):
        activities = modules.get_user_activities(request.user)
        return render(request, 'social/home_activity_view.html', {'activities':activities})


class TodoFeed(View):

    def get(self, request):
        activities_todo = modules.get_users_feed(request.user)
        notification = Notification.objects.filter(user=request.user)
        notification = NotificationFeed(notifications=notification, user=request.user)
        unread_list = notification.get_unread_notification()

        return render(request, 'social/news_feed.html', {'activities_todo':activities_todo, 'notifications':unread_list})


class PeopleView(View):

    def get(self, request):
        result = []
        if 'get_people' in request.GET and request.GET['get_people']:
            query_string = str(request.GET['get_people'])
            result = modules.find_people(query_string, request.user)
        return render(request, 'social/list_of_users.html', {'result':result})


class SendFriendRequestView(View):

    def post(self, request):
        user_id = request.POST.get("user_id")
        other_user = User.objects.get(id=int(user_id))
        Friend.objects.add_friend(request.user, other_user, message="Hi! I would like to add you!")
        return ''

