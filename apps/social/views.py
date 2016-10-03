from django.shortcuts import render
from django.views.generic import View
from forms import social_forms
from models import ProfilePictures, Notification, Vouche, Follow, TaskPicture
from ..tasks.models import TikedgeUser, UserProject, User, Tasks
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from encouragements_list import FAIL
from django.core.exceptions import ObjectDoesNotExist
import modules
from friendship.models import Friend, FriendshipRequest
from tasks_feed import NotificationFeed
from friendship.exceptions import AlreadyExistsError, AlreadyFriendsError
from django.core.exceptions import ValidationError
import global_variables
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
import json


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


class CSRFExemptView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CSRFExemptView, self).dispatch(*args, **kwargs)


class CSRFEnsureCookiesView(View):
    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super(CSRFEnsureCookiesView, self).dispatch(*args, **kwargs)


class ApiHomeActivityView(CSRFEnsureCookiesView):

    def get(self, request, *args, **kwargs):
        response = {}
        user = User.objects.get(username=request.GET.get("username"))
        activities = modules.get_user_activities_in_json_format(user)
        if activities:
            response["status"] = True
            response["activities"] = activities
        else:
            response["status"] = False
        return HttpResponse(json.dumps(response), status=201)


class ApiPictureUploadView(CSRFExemptView):

    def get(self, request):
        pass

    def post(self, request, *args, **kwargs):
        response = {}
        print request
        picture_files = request.FILES.getlist('pictureFiles[]', False)
        print picture_files
        username = request.POST.get("username")
        print username
        user = User.objects.get(username=username)
        tkduser = TikedgeUser.objects.get(user=user)
        response["status"] = False
        for each_pic in picture_files:
            picture_mod = TaskPicture(image_name=each_pic.name, task_pics=each_pic, tikede_user=tkduser)
            picture_mod.save()
            response["status"] = True
            response["picture_id"] = picture_mod.id
            response["picture_url"] = picture_mod.task_pics.url
        return HttpResponse(json.dumps(response), status=201)


class ApiAddNewPictureToTask(CSRFExemptView):

    def get(self, request):
        pass

    def post(self, request, *args, **kwargs):
        response = {}
        task_id = request.POST.get('task_id')
        picture_id = request.POST.get('pic_id')
        try:
            task_picture = TaskPicture.objects.get(id=int(picture_id))
            task = Tasks.objects.get(id=int(task_id))
            task_picture.task = task
            task_picture.save()
            response["status"] = True
        except ObjectDoesNotExist:
            response["status"] = False

        return HttpResponse(json.dumps(response), status=201)


class ApiTodoFeed(CSRFEnsureCookiesView):

    def get(self, request):
        response = {}
        username = request.GET.get("username")
        user = User.objects.get(username=username)
        feed_list = modules.transform_activities_feed_to_json(user)
        if feed_list:
            response['status'] = "true"
            response['feed'] = feed_list
        else:
             response['status'] = "false"

        return HttpResponse(json.dumps(response), status=201)


class PeopleView(View):

    def get(self, request):
        result = []
        if 'get_people' in request.GET and request.GET['get_people']:
            query_string = str(request.GET['get_people'])
            result = modules.find_people(query_string, request.user)
        return render(request, 'social/list_of_users.html', {'result':result})


class ApiPeopleView(CSRFExemptView):

    def get(self, request):
        query_string = str(request.GET.get('query_word'))
        user = User.objects.get(username=request.GET.get('username'))
        result = modules.find_people(query_string, user)
        response = {}
        if result:
            response["status"] = True
            response["found_results"] = modules.people_result_to_json(result)
        else:
            response["status"] = True

        return HttpResponse(json.dumps(response), status=201)


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


class ApiSendFriendRequestView(CSRFExemptView):

    def get(self, request):
        pass

    def post(self, request):
        user = User.objects.get(username=request.POST.get("username"))
        user_id = request.POST.get("user_id")
        other_user = TikedgeUser.objects.get(id=int(user_id))
        print other_user.user.username, other_user.user.first_name, other_user.user.last_name, other_user.user.pk
        message = "Hi! ", user.first_name, " ", user.last_name, " would like to add you as a friend!"
        response ={}
        try:
            Friend.objects.add_friend(user, other_user.user, message=message)
            friend_request = FriendshipRequest.objects.get(to_user=other_user.user)
            print friend_request
            notification = Notification(friend_request=friend_request, user=other_user.user,
                                        type_of_notification=global_variables.FRIEND_REQUEST)
            notification.save()
            response["status"] = True
        except (AlreadyFriendsError, AlreadyExistsError, ValidationError):
            pass
            print "Friends Already Exist"
            response["status"] = False
        return HttpResponse(json.dumps(response), status=201)


class AcceptFriendRequestView(View):

    def get(self, request):
        pass

    def post(self, request):
        request_id = request.POST.get("pk")
        print "Request ID %s", request_id
        friend_request = FriendshipRequest.objects.get(pk=int(request_id))
        friend_request.accept()
        return HttpResponse('')


class ApiAcceptFriendRequestView(CSRFExemptView):
    def get(self, request):
        pass

    def post(self, request):
        request_id = request.POST.get("pk")
        print "Request ID %s", request_id
        friend_request = FriendshipRequest.objects.get(pk=int(request_id))
        friend_request.accept()
        response = {}
        response["status"] = True
        return HttpResponse(json.dumps(response), status=201)


class ApiRejectFriendRequestView(CSRFExemptView):
    def get(self, request):
        pass

    def post(self, request):
        request_id = request.POST.get("pk")
        print "Request ID %s", request_id
        friend_request = FriendshipRequest.objects.get(pk=int(request_id))
        friend_request.reject()
        response = {}
        response["status"] = True
        return HttpResponse(json.dumps(response), status=201)


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









