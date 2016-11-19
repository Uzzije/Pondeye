from django.shortcuts import render
from django.views.generic import View
from forms import social_forms
from models import ProfilePictures, Notification, Vouche, Follow, PictureSet, Picture, VoucheMilestone
from ..tasks.models import TikedgeUser, UserProject, User, Tasks, Milestone
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from encouragements_list import FAIL
from django.core.exceptions import ObjectDoesNotExist
import modules
from ..tasks import modules as task_modules
from friendship.models import Friend, FriendshipRequest
from tasks_feed import NotificationFeed
from friendship.exceptions import AlreadyExistsError, AlreadyFriendsError
from django.core.exceptions import ValidationError
import global_variables
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
import json
from django.contrib import messages


class CSRFExemptView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CSRFExemptView, self).dispatch(*args, **kwargs)


class CSRFEnsureCookiesView(View):
    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super(CSRFEnsureCookiesView, self).dispatch(*args, **kwargs)


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
        existing_milestones = task_modules.get_user_milestones(request.user)
        user_picture_form = social_forms.PictureUploadForm()

        return render(request, 'social/upload_picture.html', {'user_picture_form':user_picture_form,
                                                              'existing_milestones':existing_milestones})

    def post(self, request):
        user_picture_form = social_forms.PictureUploadForm(request.POST, request.FILES)

        if user_picture_form.is_valid() and 'type_of_picture' in request.POST:
            tkduser = TikedgeUser.objects.get(user=request.user)
            picture_file = request.FILES.get('picture', False)
            milestone_name = request.POST.get('milestone_name')
            milestone = Milestone.objects.get(name_of_milestone=milestone_name)
            if request.POST.get("type_of_picture") == global_variables.BEFORE_PICTURE:
                is_before = True
                # check that user is not creating concurrent before for current milestone
                try:
                    PictureSet.objects.get(milestone=milestone, after_picture=None)
                    messages.error(request, 'Sorry we need an after picture for %s milestone' % milestone.name_of_milestone)
                    existing_milestones = task_modules.get_user_milestones(request.user)
                    return render(request, 'social/upload_picture.html', {'user_picture_form':user_picture_form,
                                                                          'existing_milestones':existing_milestones})
                except ObjectDoesNotExist:
                    pass
            else:
                is_before = False
            picture_mod = Picture(image_name=picture_file.name,
                                   milestone_pics=picture_file, tikedge_user=tkduser, is_before=is_before)
            picture_mod.save()
            if is_before:
                pic_set = PictureSet(before_picture=picture_mod, milestone=milestone, tikedge_user=tkduser)
                pic_set.save()
                messages.success(request, 'Cool! the before visual entry added to %s milestone' % milestone.name_of_milestone)
            else:
                try:
                    pic_set = PictureSet.objects.get(milestone=milestone, after_picture=None, tikedge_user=tkduser)
                    pic_set.after_picture = picture_mod
                    pic_set.save()
                    messages.success(request, 'Great Job! the after visual entry added to %s milestone' % milestone.name_of_milestone)
                except ObjectDoesNotExist:
                    existing_milestones = task_modules.get_user_milestones(request.user)
                    messages.error(request, 'Hey we need a before visual entry to wow the crowd')
                    return render(request, 'social/upload_picture.html', {'user_picture_form':user_picture_form,
                                                              'existing_milestones':existing_milestones})
            return HttpResponseRedirect(reverse('tasks:home'))
        existing_milestones = task_modules.get_user_milestones(request.user)
        messages.error(request, 'Oops, I think you forgot to upload a picture')
        return render(request, 'social/upload_picture.html', {'user_picture_form':user_picture_form,
                                                              'existing_milestones':existing_milestones})

class HomeActivityView(View):

    def get(self, request):
        activities = modules.get_user_activities(request.user)
        return render(request, 'social/home_activity_view.html', {'activities':activities})


class TodoFeed(View):

    def get(self, request):
        all_feeds = modules.get_users_feed(request.user)
        notification = Notification.objects.filter(user=request.user)
        notification = NotificationFeed(notifications=notification, user=request.user)
        unread_list = notification.get_unread_notification()
        return render(request, 'social/news_feed.html', {'all_feeds':all_feeds, 'notifications':unread_list})


class PeopleView(View):

    def get(self, request):
        result = []
        if 'get_people' in request.GET and request.GET['get_people']:
            query_string = str(request.GET['get_people'])
            result = modules.find_people(query_string, request.user)
        return render(request, 'social/list_of_users.html', {'result':result})


class SendFriendRequestView(View):

    def get(self, request):
        pass

    def post(self, request):
        user_id = request.POST.get("user_id")
        other_user = TikedgeUser.objects.get(id=int(user_id))
        print other_user.user.username, other_user.user.first_name, other_user.user.last_name
        message = "Hi! ", request.user.first_name, " ", request.user.last_name, " would like to add you as a friend!"
        try:
            Friend.objects.add_friend(request.user, other_user.user, message=message)
            friend_request = FriendshipRequest.objects.get(pk=other_user.pk)
            notification = Notification(friend_request=friend_request, user=other_user.user,
                                        type_of_notification=global_variables.FRIEND_REQUEST)
            notification.save()
        except (AlreadyFriendsError, AlreadyExistsError, ValidationError):
            pass
            print "Friends Already Exist"
        return HttpResponse('')


class AcceptFriendRequestView(View):

    def get(self, request):
        pass

    def post(self, request):
        request_id = request.POST.get("pk")
        print "Request ID %s", request_id
        friend_request = FriendshipRequest.objects.get(pk=int(request_id))
        friend_request.accept()
        return HttpResponse('')


class RejectFriendRequestView(View):

    def get(self, request):
        pass

    def post(self, request):
        request_id = request.POST.get("pk")
        print "Request ID %s", request_id
        friend_request = FriendshipRequest.objects.get(pk=int(request_id))
        friend_request.reject()
        return HttpResponse('')


class FriendRequestView(View):

    def get(self, request):
        friend_request = Friend.objects.requests(request.user)
        print friend_request
        return render(request, 'social/friend_request.html', {'friend_request':friend_request})


class ApiFriendRequestView(CSRFExemptView):

    def get(self, request):
        user = User.objects.get(username=request.GET.get("username"))
        friend_request = Friend.objects.requests(user)
        print friend_request, " frienddder"
        json_result = modules.friend_request_to_json(friend_request, user)
        response = {}
        if json_result:
            response["status"] = True
            response["result"] = json_result
        else:
            response["status"] = False
        return HttpResponse(json.dumps(response), status=201)


class CreateVouch(View):

    def post(self, request, *args, **kwargs):
        response = {}
        milestone_id = request.POST.get("mil_id")
        milestone = Milestone.objects.get(id=int(milestone_id))
        user = TikedgeUser.objects.get(user=request.user)
        try:
            vouch_obj = VoucheMilestone.objects.get(tasks=milestone)
        except ObjectDoesNotExist:
            vouch_obj = VoucheMilestone(tasks=milestone)
            vouch_obj.save()
        if user not in vouch_obj.users.all():
            vouch_obj.users.add(user)
            vouch_obj.save()
            response["status"] = True
        else:
            response["status"] = False
        return HttpResponse(json.dumps(response), status=201)


class ApiCreateVouch(CSRFExemptView):

    def get(self, request, *args, **kwargs):
        return HttpResponse('')

    def post(self, request, *args, **kwargs):
        response = {}
        print "reaching here"
        task_id = request.POST.get("task_id")
        task = Tasks.objects.get(id=task_id)
        username = request.POST.get("username")
        user = User.objects.get(username=username)
        tikedge_user = TikedgeUser.objects.get(user=user)
        try:
            vouch_obj = Vouche.objects.get(tasks=task)
        except ObjectDoesNotExist:
            vouch_obj = Vouche(tasks=task)
            vouch_obj.save()
        if not tikedge_user in vouch_obj.users.all():
            response["status"] = "true"
            vouch_obj.users.add(tikedge_user)
            vouch_obj.save()
        else:
            response["status"] = "false"
        response["count"] = vouch_obj.users.all().count()
        return HttpResponse(json.dumps(response), status=201)


class ApiCreateFollow(CSRFExemptView):

    def get(self, request, *args, **kwargs):
        return HttpResponse('')

    def post(self, request, *args, **kwargs):
        response = {}
        task_id = request.POST.get("task_id")
        task = Tasks.objects.get(id=task_id)
        username = request.POST.get("username")
        user = User.objects.get(username=username)
        tikedge_user = TikedgeUser.objects.get(user=user)
        try:
            follow_obj = Follow.objects.get(tasks=task.project)
        except ObjectDoesNotExist:
            follow_obj = Follow(tasks=task.project)
            follow_obj.save()
        if not tikedge_user in follow_obj.users.all():
            response["status"] = "true"
            follow_obj.users.add(tikedge_user)
            follow_obj.save()
        else:
            response["status"] = "false"
        response["count"] = follow_obj.users.all().count()
        return HttpResponse(json.dumps(response), status=201)









