from django.shortcuts import render
from django.views.generic import View
from forms import social_forms, pond_form
from models import (Notification, Follow, PictureSet, Picture, VoucheMilestone, SeenMilestone,
                    JournalPost, JournalComment, SeenProject, ProfilePictures, Pond, PondRequest,
                    PondMembership, PondSpecificProject, User)
from ..tasks.models import TikedgeUser, UserProject, Milestone, TagNames
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
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
from django.db.models import Q
from search_module import find_everything, find_project_and_milestone_by_tag
from braces.views import LoginRequiredMixin
from ..tasks.global_variables_tasks import TAG_NAMES_LISTS
from datetime import datetime


class CSRFExemptView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CSRFExemptView, self).dispatch(*args, **kwargs)


class CSRFEnsureCookiesView(View):
    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super(CSRFEnsureCookiesView, self).dispatch(*args, **kwargs)


class ApiNewPondEntryView(CSRFExemptView):

    def post(self, request, *args, **kwargs ):
        response = {}
        try:
            username = request.POST.get("username")
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            response["status"] = False
            response["error"] = "Log back in and try again!"
            return HttpResponse(json.dumps(response), status=201)
        pond_name = request.POST.get('name_of_pond')
        if len(pond_name) > 245:
            response["status"] = False
            count_exceed = len(pond_name) - global_variables.POND_NAME_CHAR_COUNT
            response["error"] = "Exceeds pond's name maximum character count by %s." % str(count_exceed)
            return HttpResponse(json.dumps(response), status=201)
        purpose = request.POST.get('purpose')
        if len(purpose) > 100:
            response["status"] = False
            count_exceed = len(purpose) - global_variables.POND_PURPOSE_CHAR_COUNT
            response["error"] = "Exceeds purpose maximum character count by %s." % str(count_exceed)
            return HttpResponse(json.dumps(response), status=201)
        tag_obj = request.POST.get('tags')
        tags = tag_obj.split(",")
        pond = Pond(name_of_pond=pond_name, purpose=purpose,
                    pond_creator=task_modules.get_tikedge_user(user))
        pond.save()
        for item in tags:
            print tags, " tags why"
            try:
                item_obj = TagNames.objects.get(name_of_tag=item)
            except ObjectDoesNotExist:
                item_obj = TagNames(name_of_tag=item)
                item_obj.save()
            pond.tags.add(item_obj)
        pond.pond_members.add(task_modules.get_tikedge_user(user))
        pond.save()
        pond_membership = PondMembership(user=task_modules.get_tikedge_user(user),
                                         pond=pond)
        pond_membership.save()
        response["status"] = True
        return HttpResponse(json.dumps(response), status=201)


class ApiPictureUploadView(LoginRequiredMixin, View):

    def get(self, request):
        response = {}
        try:
            username = request.POST.get("username")
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            response["status"] = False
            response["error"] = "Log back in and try again!"
            return HttpResponse(json.dumps(response), status=201)
        existing_milestones = task_modules.get_user_milestones(user)
        if existing_milestones:
	        response["status"] = True
	        response["has_mil"] = True
	        response["milestone"] = existing_milestones
        else:
	        response["status"] = False
	        response["error"] = "You need to have a milestone to capture your event!"
	        response["has_mil"] = False
		return HttpResponse(json.dumps(response), status=201)


    def post(self, request):
        response = {}
        response["status"] = False
        try:
            username = request.POST.get("username")
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            response["error"] = "Log back in and try again!"
            return HttpResponse(json.dumps(response), status=201)
        tkduser = TikedgeUser.objects.get(user=user)
        picture_file = request.FILES.get('picture', False)
        if not modules.file_is_picture(picture_file):
            response["error"] = "Hey visual must be either jpg, jpeg or png file!"
            return HttpResponse(json.dumps(response), status=201)
        milestone_name = request.POST.get('milestone_name')
        milestone = Milestone.objects.get(id=milestone_name)
        if request.POST.get("type_of_picture") == global_variables.BEFORE_PICTURE:
            is_before = True
            # check that user is not creating concurrent before for current milestone
            try:
                PictureSet.objects.get(milestone=milestone, after_picture=None, is_deleted=False)
                response["error"] = 'Sorry we first need an after picture for %s milestone' % milestone.name_of_milestone
                return HttpResponse(json.dumps(response), status=201)
            except ObjectDoesNotExist:
                pass
        else:
            is_before = False
        picture_file.file = modules.resize_image(picture_file)
        picture_mod = Picture(image_name=picture_file.name,
                               milestone_pics=picture_file, tikedge_user=tkduser, is_before=is_before)
        picture_mod.save()
        if is_before:
            pic_set = PictureSet(before_picture=picture_mod, milestone=milestone, tikedge_user=tkduser)
            pic_set.save()
            day_entry = tkduser.journalpost_set.all().count()
            new_journal_entry = JournalPost(
                                            entry_blurb=modules.get_journal_message(global_variables.BEFORE_PICTURE,
                                                                                    milestone=milestone.blurb),
                                                                                    day_entry=day_entry + 1,
                                                                                    event_type=global_variables.BEFORE_PICTURE,
                                                                                    is_picture_set=True,
                                                                                    picture_set_entry=pic_set,
                                                                                    user=tkduser
                                                                                    )
            new_journal_entry.save()
        else:
            try:
                pic_set = PictureSet.objects.get(milestone=milestone, after_picture=None, tikedge_user=tkduser, is_deleted=False)
                pic_set.after_picture = picture_mod
                pic_set.save()
                day_entry = tkduser.journalpost_set.all().count()
                new_journal_entry = JournalPost(
                                            entry_blurb=modules.get_journal_message(global_variables.AFTER_PICTURE,
                                                                                    milestone=milestone.blurb),
                                            day_entry=day_entry + 1,
                                            event_type=global_variables.AFTER_PICTURE,
                                            is_picture_set=True,
                                             picture_set_entry=pic_set
                                            )
                new_journal_entry.save()
                messages.success(request, 'Great Job! The after visual entry added to %s milestone' % milestone.blurb)
            except ObjectDoesNotExist:
                response["error"] = 'Hey we need a before visual entry before an after visual entry. This wow the crowd!'
                return HttpResponse(json.dumps(response), status=201)
	    response["status"] = True
        return HttpResponse(json.dumps(response), status=201)

