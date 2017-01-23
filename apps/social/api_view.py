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


class ApiPictureUploadView(CSRFExemptView):

    def get(self, request):
        response = {}
        try:
            username = request.GET.get("username")
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
        milestone = Milestone.objects.get(id=int(milestone_name))
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


class  ApiEditPictureSetView(CSRFExemptView):
    """
    Remove Complete Pictures. Edit Pictures Without After Shot (i.e Delete Them or Change Them).
    """

    def get(self, request):
        response = {}
        response["status"] = False
        try:
            username = request.GET.get("username")
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            response["error"] = "Log back in and try again!"
            return HttpResponse(json.dumps(response), status=201)
        tikedge_user = TikedgeUser.objects.get(user=user)
        user_picture_set = PictureSet.objects.filter(tikedge_user=tikedge_user, is_deleted=False)
        picture_set = []
        for each_pic in user_picture_set:
            if each_pic.after_picture:
                hasPic = True
            else:
                hasPic = True
            picture_set.append({
                'before_picture':{'id':each_pic.before_picture.id,
                                  'url':each_pic.before_picture.milestone_pics.url,
                                  },
                'after_picture':{'id':each_pic.after_picture.id,
                                 'url':each_pic.after_picture.milestone_pics.url
                                 },
                'blurb':each_pic.milestone.blurb,
                'id':each_pic.id,
                'slug':each_pic.milestone.slug,
                'hidden':False,
                'hasAfterPicture':hasPic
            })
        response["user_picture_set"] = picture_set
        response["status"] = True
        return HttpResponse(json.dumps(response), status=201)

    def post(self, request):
        response = {}
        response["status"] = False
        try:
            username = request.POST.get("username")
            User.objects.get(username=username)
        except ObjectDoesNotExist:
            response["error"] = "Log back in and try again!"
            return HttpResponse(json.dumps(response), status=201)
        if 'change_picture_after' in request.POST:
            pic_set_id = request.POST.get("change_picture_after")
            picture = Picture.objects.get(id=int(pic_set_id))
            pic_file = request.FILES.get('picture', False)
            if modules.file_is_picture(pic_file):
                pic_file.file = modules.resize_image(pic_file)
                picture.milestone_pics = pic_file
                picture.image_name = pic_file.name
                picture.last_edited = datetime.now()
                picture.save()
            else:
                response["error"] = 'Hey visual must be either jpg, jpeg or png file!'
                return HttpResponse(json.dumps(response), status=201)
        if 'change_picture_before' in request.POST:
            pic_set_id = request.POST.get("change_picture_before")
            picture = Picture.objects.get(id=int(pic_set_id))
            pic_file = request.FILES.get('picture', False)
            if modules.file_is_picture(pic_file):
                pic_file.file = modules.resize_image(pic_file)
                picture.milestone_pics = pic_file
                picture.image_name = pic_file.name
                picture.last_edited = datetime.now()
                picture.save()
            else:
                response["error"] = 'Hey visual must be either jpg, jpeg or png file!'
                return HttpResponse(json.dumps(response), status=201)
        if 'delete_picture_after' in request.POST:
            pic_id = request.POST.get("delete_picture_after")
            picture = Picture.objects.get(id=int(pic_id))
            picture.is_deleted = True
            picture.last_edited = datetime.now()
            picture.save()
            picture_set = PictureSet.objects.get(after_picture=picture)
            picture_set.after_picture = None
            picture_set.save()
        if 'delete_picture_before' in request.POST:
            pic_id = request.POST.get("delete_picture_before")
            picture = Picture.objects.get(id=int(pic_id))
            picture.is_deleted = True
            picture.last_edited = datetime.now()
            picture.save()
            picture_set = PictureSet.objects.get(before_picture=picture)
            picture_set.before_picture = None
            picture_set.is_deleted = True
            picture_set.save()
        response["status"] = True
        return HttpResponse(json.dumps(response), status=201)


class ApiDeletePictureSet(CSRFExemptView):

    def post(self, request):
        try:
            pic_set_id = request.POST.get("pic_set_id")
            pic_set = PictureSet.objects.get(id=int(pic_set_id))
            pic_set.is_deleted = True
            pic_set.save()
            response = {'status':True}
        except ObjectDoesNotExist:
            response = {'status':False}
        return HttpResponse(json.dumps(response))


class ApiEditPondView(CSRFExemptView):

    def get(self, request):
        response = {}
        response["status"] = False
        try:
            username = request.GET.get("username")
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            response["error"] = "Log back in and try again!"
            return HttpResponse(json.dumps(response), status=201)
        tikedge_user = TikedgeUser.objects.get(user=user)
        ponds = Pond.objects.filter(pond_members__user=tikedge_user.user, is_deleted=False)
        pond_list = []
        for pond in ponds:
            tag_list = []
            pond_mem_list = []
            for item in pond.tags.all():
                tag_list.append(item.name_of_tag)
            for pond_mem in pond.pond_members.all():
                if pond_mem != pond.pond_creator:
                    pond_mem_list.append({
                        'first_name':pond_mem.user.first_name,
                        'last_name':pond_mem.user.last_name,
                        'username':pond_mem.user.username
                    })
            pond_list.append({
                'id':pond.id,
                'blurb':pond.blurb,
                'slug':pond.slug,
                'pond_list':tag_list,
                'pond_members': pond_mem_list,
                'purpose':pond.purpose
            })
        if pond_list:
            response["status"] = True
        response["pond_list"] = pond_list
        return HttpResponse(json.dumps(response), status=201)

    def post(self, request):
        response = {"status":False}
        if 'pond_id' in request.POST:
            pond_id = request.POST.get("pond_id")
            pond = Pond.objects.get(id=int(pond_id))
            pond.is_deleted = True
            pond.save()
            response = {"status":True}
        return HttpResponse(json.dumps(response), status=201)


class ApiEditIndividualPondView(CSRFExemptView):

    def get(self, request, *args, **kwargs):
        slug = request.GET.get("slug")
        response = {}
        response["status"] = False
        pond = Pond.objects.get(slug=slug)
        response['name_of_pond'] = pond.name_of_pond,
        response['purpose'] = pond.purpose,
        select_tags = modules.get_tag_list(pond.tags.all())
        pond_members = pond.pond_members.all()
        response["select_tags"] = select_tags
        pond_members_list = []
        for each_mem in pond_members:
            pond_members_list.append({
                'pond_member_first_name':each_mem.user.first_name,
                'pond_member_last_name':each_mem.user.last_name,
                'slug':each_mem.slug,
                'id':each_mem.id
            })

        response["pond_members"] = pond_members_list
        response["status"] = True
        return HttpResponse(json.dumps(response), status=201)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = False
        pond_id = request.POST.get("pond_id")
        pond = Pond.objects.get(id=int(pond_id))
        pond_name = request.POST.get('name_of_pond')
        purpose = request.POST.get('purpose')
        tags_obj = request.POST.get('tags')
        tags = tags_obj.split(",")
        ponders_obj = request.POST.get('ponders')
        ponders = ponders_obj.split(",")
        pond.name_of_pond = pond_name
        pond.purpose = purpose
        pond.save()
        for item in pond.tags.all():
            pond.tags.remove(item)
        pond.save()
        for item in tags:
            try:
                item_obj = TagNames.objects.get(name_of_tag=item)
            except ObjectDoesNotExist:
                item_obj = TagNames(name_of_tag=item)
                item_obj.save()
            pond.tags.add(item_obj)
        for pd in ponders:
            tik = TikedgeUser.objects.get(id=pd)
            pond.pond_members.remove(tik)
        pond.save()
        response["status"] = True
        return HttpResponse(json.dumps(response), status=201)