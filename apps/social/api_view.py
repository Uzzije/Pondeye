from django.views.generic import View
from models import (Notification, Follow, VoucheMilestone, SeenMilestone,
                     SeenProject, Pond, PondRequest,
                    PondMembership, User, ProgressPicture,
                    ProgressPictureSet, ProgressImpressedCount, SeenProgress, VoucheProject)
from ..tasks.models import TikedgeUser, UserProject, Milestone, TagNames
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist
import modules
from ..tasks import modules as task_modules
import global_variables
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
import json

from django.db.models import Q
from search_module import find_everything, search_result_jsonified
from image_modules import pondeye_image_filter
from django.utils import timezone



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
        pond = Pond(name_of_pond=pond_name, purpose=purpose,
                    pond_creator=task_modules.get_tikedge_user(user))
        pond.save()
        tag_obj = request.POST.get('tags')
        if len(tag_obj) > 0:
            tags = tag_obj.split(",")
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

'''
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
        projects = task_modules.api_get_user_projects(user)
        if projects:
            response['has_proj'] = True
            response["status"] = True
            response["projects"] = projects
        else:
	        response["status"] = False
	        response["error"] = "Create a goal, then use pictures to capture the progress of that goal!"
	        response["has_proj"] = False
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
        dec_picture_file = request.POST.get('picture')
        picture_file = modules.get_picture_from_base64(dec_picture_file)
        if not picture_file:
            response["error"] = "Hey picture must be either jpg, jpeg or png file! ", dec_picture_file
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
            response['status'] = True
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
                response["error"] = 'Hey we need a before visual entry before an after visual entry!'
                return HttpResponse(json.dumps(response), status=201)
	    response["status"] = True
        return HttpResponse(json.dumps(response), status=201)

'''


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
        projects = task_modules.api_get_user_projects(user)
        if projects:
            response['has_proj'] = True
            response["status"] = True
            response["projects"] = projects
        else:
	        response["status"] = False
	        response["error"] = "Create a goal, then use pictures to capture the progress of that goal!"
	        response["has_proj"] = False
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
        dec_picture_file = request.POST.get('picture')
        picture_file = modules.get_picture_from_base64(dec_picture_file)
        if not picture_file:
            response["error"] = "Hey picture must be either jpg, jpeg or png file! ", dec_picture_file
            return HttpResponse(json.dumps(response), status=201)
        progress_name = request.POST.get('progress_name')
        if len(progress_name) > 250:
            response["error"] = "Hey description of progress must be less that 250 characters!"
            return HttpResponse(json.dumps(response), status=201)
        picture_file.file = modules.resize_image(picture_file)
        picture_mod = ProgressPicture(image_name=picture_file.name,
                               picture=picture_file, name_of_progress=progress_name)
        picture_mod.save()
        pondeye_image_filter(picture_mod.picture.name)
        impress_count = ProgressImpressedCount(tasks=picture_mod)
        impress_count.save()
        seen_progress = SeenProgress(tasks=picture_mod)
        seen_progress.save()
        project = UserProject.objects.get(id=int(request.POST.get("project_id")))
        progress_set = ProgressPictureSet.objects.get(project=project)
        progress_set.is_empty = False
        progress_set.list_of_progress_pictures.add(picture_mod)
        progress_set.save()
        response["status"] = True
        modules.new_goal_or_progress_added_notification_to_pond(progress_set.project, is_new_project=False)
        return HttpResponse(json.dumps(response), status=201)

'''
class  ApiEditPictureSetView(CSRFExemptView):
    """
    Remove Complete Pictures. Edit Pictures Without After Shot (i.e Delete Them or Change Them).
    """

    def get(self, request):
        """
        Edit Pond Data get the neccessary Informations
        :param request: 
        :return: 
        """
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
                picture_set.append({
                   'before_picture':{'id':each_pic.before_picture.id,
                                     'url':global_variables.CURRENT_URL + each_pic.before_picture.milestone_pics.url,
                                     },
                   'after_picture':{'id':each_pic.after_picture.id,
                                    'url':global_variables.CURRENT_URL + each_pic.after_picture.milestone_pics.url
                                    },
                   'blurb':each_pic.milestone.blurb,
                   'id':each_pic.id,
                   'slug':each_pic.milestone.slug,
                   'hidden':False,
                   'hasAfterPicture':hasPic
               })
            else:
                hasPic = False
                picture_set.append({
                    'before_picture':{'id':each_pic.before_picture.id,
                                      'url':global_variables.CURRENT_URL + each_pic.before_picture.milestone_pics.url,
                                      },
                    'blurb':each_pic.milestone.blurb,
                    'id':each_pic.id,
                    'slug':each_pic.milestone.slug,
                    'hidden':False,
                    'hasAfterPicture':hasPic
                })
        response["user_picture_set"] = picture_set
        if picture_set:
            response["has_set"] = True
        else:
            response["has_set"] = False
        response["status"] = True
        return HttpResponse(json.dumps(response), status=201)

    def post(self, request):
        """
        Edit Pond Data
        :param request: 
        :return: 
        """
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
            pic = request.POST.get('picture')
            pic_file = modules.get_picture_from_base64(pic)
            if pic_file:
                pic_file.file = modules.resize_image(pic_file)
                picture.milestone_pics = pic_file
                picture.image_name = pic_file.name
                picture.last_edited = timezone.now()
                picture.save()
                response['status'] = True
            else:
                response["error"] = 'Hey after visual must be either jpg, jpeg or png file!'
                return HttpResponse(json.dumps(response), status=201)
        elif 'change_picture_before' in request.POST:
            pic_set_id = request.POST.get("change_picture_before")
            picture = Picture.objects.get(id=int(pic_set_id))
            pic = request.POST.get('picture')
            pic_file = modules.get_picture_from_base64(pic)
            if pic_file:
                pic_file.file = modules.resize_image(pic_file)
                picture.milestone_pics = pic_file
                picture.image_name = pic_file.name
                picture.last_edited = timezone.now()
                picture.save()
                response['status'] = True
            else:
                response["error"] = 'Hey before visual must be either jpg, jpeg or png file!'
                return HttpResponse(json.dumps(response), status=201)
        elif 'delete_picture_after' in request.POST:
            pic_id = request.POST.get("delete_picture_after")
            picture = Picture.objects.get(id=int(pic_id))
            picture.is_deleted = True
            picture.last_edited = timezone.now()
            picture.save()
            picture_set = PictureSet.objects.get(after_picture=picture)
            picture_set.after_picture = None
            picture_set.save()
        elif 'delete_picture_before' in request.POST:
            pic_id = request.POST.get("delete_picture_before")
            picture = Picture.objects.get(id=int(pic_id))
            picture.is_deleted = True
            picture.last_edited = timezone.now()
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
'''


class ApiEditPictureSetView(CSRFExemptView):

    def get(self, request):
        """
        Edit Pond Data get the neccessary Informations
        :param request:
        :return:
        """
        response = {}
        response["status"] = False
        try:
            username = request.GET.get("username")
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            response["error"] = "Log back in and try again!"
            return HttpResponse(json.dumps(response), status=201)
        progress_set = ProgressPictureSet.objects.filter(project__user__user=user, project__is_deleted=False)
        curr_timezone = request.GET.get("timezone")
        list_of_progress_sets = modules.get_progress_set(progress_set, curr_timezone)
        response['user_picture_set'] = list_of_progress_sets
        if list_of_progress_sets:
            response['has_set'] = True
        else:
            response['has_set'] = False
        return HttpResponse(json.dumps(response), status=201)

    def post(self, request):
        try:
            change_text = request.POST.get("change_text")
            pic_id = request.POST.get("pic_id")
            progress = ProgressPicture.objects.get(id=int(pic_id))
            if len(change_text) > 0:
                progress.name_of_progress = change_text
                progress.save()
            else:
                progress = ProgressPicture.objects.get(id=int(pic_id))
                progress.is_deleted = True
                progress.save()
                progress_set = ProgressPictureSet.objects.get(list_of_progress_pictures=progress)
                if progress_set.picture_set_count() == 0:
                    progress_set.is_empty = True
                    progress_set.save()
            response = {'status':True}
        except ObjectDoesNotExist:
            response = {'status':False}
        return HttpResponse(json.dumps(response))


class ApiEditPondView(CSRFExemptView):

    def get(self, request):
        """
        Grab data for loading to Pond Edit View in App
        :param request:
        :return:
        """
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
                        'username':pond_mem.user.username,
                        'id':pond_mem.id
                    })
            pond_list.append({
                'id':pond.id,
                'name':pond.name_of_pond,
                'slug':pond.slug,
                'tag_list':tag_list,
                'pond_members': pond_mem_list,
                'purpose':pond.purpose
            })
        if pond_list:
            response['has_pond'] = True
        else:
            response['has_pond'] = False
        response["status"] = True
        response["pond_list"] = pond_list
        return HttpResponse(json.dumps(response), status=201)

    def post(self, request):
        """
        Post call for delete a pond
        :param request:
        :return:
        """
        response = {}
        response["status"] = False
        try:
            username = request.POST.get("username")
            User.objects.get(username=username)
        except ObjectDoesNotExist:
            response["error"] = "Log back in and try again!"
            return HttpResponse(json.dumps(response), status=201)
        response = {"status":False, "error":"Something Went Wrong"}
        if 'pond_id' in request.POST:
            pond_id = request.POST.get("pond_id")
            pond = Pond.objects.get(id=int(pond_id))
            pond.is_deleted = True
            pond.save()
            response = {"status":True}
        return HttpResponse(json.dumps(response), status=201)


class ApiEditIndividualPondView(CSRFExemptView):

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
        try:
            if tags_obj:
                for item in tags:
                    try:
                        item_obj = TagNames.objects.get(name_of_tag=item)
                    except ObjectDoesNotExist:
                        item_obj = TagNames(name_of_tag=item)
                        item_obj.save()
                    pond.tags.add(item_obj)
        except ValueError:
            pass
        try:
            for pd in ponders:
                tik = TikedgeUser.objects.get(id=int(pd))
                pond.pond_members.remove(tik)
                pond_membership = PondMembership.objects.get(user=tik, pond=pond, date_removed=None)
                pond_membership.date_removed = timezone.now()
                pond_membership.save()
            pond.save()
        except ValueError:
            pass
        response["status"] = True
        return HttpResponse(json.dumps(response), status=201)


class ApiTodoFeed(CSRFExemptView):

    def get(self, request):
        response = {}
        response["status"] = False
        try:
            username = request.GET.get("username")
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            response["error"] = "Log back in and try again!"
            return HttpResponse(json.dumps(response), status=201)
        timezone = request.GET.get('timezone')
        all_feeds = modules.get_users_feed_json(user, local_timezone=timezone)
        response["status"] = True
        response["all_feeds"] = all_feeds
        return HttpResponse(json.dumps(response), status=201)


class ApiCreateVouch(CSRFExemptView):

    def post(self, request, *args, **kwargs):
        response = {}
        proj_id = request.POST.get("proj_id")
        proj = UserProject.objects.get(id=int(proj_id))
        try:
            username = request.POST.get("username")
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            response["status"] = False
            response["error"] = "Log back in and try again!"
            return HttpResponse(json.dumps(response), status=201)
        user = TikedgeUser.objects.get(user=user)
        user_response = request.POST.get("user_response")
        try:
            vouch_obj = VoucheProject.objects.get(tasks=proj)
            if user in vouch_obj.users.all() and proj.is_live and \
                            user_response == global_variables.NO_USER_WILL_NOT_COMPLETE_GOAL: #if user changes his mind
                vouch_obj.users.remove(user)
                vouch_obj.save()
                response["status"] = True
                response["count"] = vouch_obj.users.all().count()
                return HttpResponse(json.dumps(response), status=201)
        except ObjectDoesNotExist:
            vouch_obj = VoucheProject(tasks=proj)
            vouch_obj.save()
        if user not in vouch_obj.users.all() and (user != proj.user) and proj.is_live and \
                        user_response == global_variables.YES_USER_WILL_COMPLETE_GOAL:
            vouch_obj.users.add(user)
            vouch_obj.save()
            notif_message = "%s %s believes that you will complete this goal: %s" \
                            % (user.user.first_name, user.user.last_name, proj.name_of_project)
            try:
                Notification.objects.get(user=proj.user.user, name_of_notification=notif_message, id_of_object=vouch_obj.id,
                                                                    type_of_notification=global_variables.NEW_PROJECT_VOUCH)
            except ObjectDoesNotExist:
                vouch_notif = Notification(user=proj.user.user, name_of_notification=notif_message, id_of_object=vouch_obj.id,
                                                    type_of_notification=global_variables.NEW_PROJECT_VOUCH)
                vouch_notif.save()

            response["status"] = True
            response["count"] = vouch_obj.get_count()
        else:
            if user != proj.user:
                if not proj.is_live:
                    response["status"] = False
                    response["error"] = "Can't vote on inactive goal!"
                elif user_response == global_variables.NO_USER_WILL_NOT_COMPLETE_GOAL:
                    response['status'] = True
                else:
                    response["error"] = "Vote already noted"
                    response['status'] = False
            else:
                response["error"] = "Can't vote on your own goal!"
                response['status'] = False
        try:
            view = SeenProject.objects.get(tasks=proj)
        except ObjectDoesNotExist:
            view = SeenProject(tasks=proj)
            view.save()
        if user not in view.users.all():
            view.users.add(user)
            view.save()
        response["count"] = vouch_obj.get_count()
        print "Tried to print vouch!!!!!!\n"
        return HttpResponse(json.dumps(response), status=201)


class ApiCreateFollow(CSRFExemptView):

    def get(self, request, *args, **kwargs):
        return HttpResponse('')

    def post(self, request, *args, **kwargs):
        response = {}
        try:
            username = request.POST.get("username")
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            response["status"] = False
            response["error"] = "Log back in and try again!"
            return HttpResponse(json.dumps(response), status=201)
        proj_id = request.POST.get("proj_id")
        project = UserProject.objects.get(id=int(proj_id))
        tikedge_user = TikedgeUser.objects.get(user=user)
        try:
            follow_obj = Follow.objects.get(tasks=project)
            if tikedge_user in follow_obj.users.all() and project.is_live:
                follow_obj.users.remove(tikedge_user)
                follow_obj.save()
                response["status"] = "unfollow"
                response["count"] = follow_obj.users.all().count()
                return HttpResponse(json.dumps(response), status=201)
        except ObjectDoesNotExist:
            follow_obj = Follow(tasks=project)
            follow_obj.save()
        if tikedge_user != project.user and project.is_live:
            response["status"] = True
            follow_obj.users.add(tikedge_user)
            follow_obj.save()
            notif_mess = "%s %s is following your goal: %s" % (tikedge_user.user.first_name,
                                                              tikedge_user.user.last_name, project.name_of_project)
            try:
                Notification(user=project.user.user, name_of_notification=notif_mess, id_of_object=follow_obj.id,
                                                        type_of_notification=global_variables.NEW_PROJECT_INTERESTED)
            except ObjectDoesNotExist:
                follow_notif = Notification(user=project.user.user, name_of_notification=notif_mess, id_of_object=follow_obj.id,
                                        type_of_notification=global_variables.NEW_PROJECT_INTERESTED)
                follow_notif.save()
        response["count"] = follow_obj.users.all().count()
        return HttpResponse(json.dumps(response), status=201)


class ApiCreateImpressed(CSRFExemptView):

    def get(self, request, *args, **kwargs):
        return HttpResponse('')

    def post(self, request, *args, **kwargs):
        response = {}
        try:
            username = request.POST.get("username")
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            response["status"] = False
            response["error"] = "Log back in and try again!"
            return HttpResponse(json.dumps(response), status=201)
        progress_id = request.POST.get("progress_id")
        progress_set_id = request.POST.get('progress_set_id')
        progress_set = ProgressPictureSet.objects.get(id=int(progress_set_id))
        progress = ProgressPicture.objects.get(id=int(progress_id))
        tikedge_user = TikedgeUser.objects.get(user=user)
        impressed_count = ProgressImpressedCount.objects.get(tasks=progress)
        if tikedge_user in impressed_count.users.all():
            impressed_count.users.remove(tikedge_user)
            impressed_count.save()
            response["status"] = True
            response["count"] = impressed_count.get_count()
            return HttpResponse(json.dumps(response), status=201)
        if tikedge_user != progress_set.project.user:
            response["status"] = True
            impressed_count.users.add(tikedge_user)
            impressed_count.save()
            name_of_notif = "%s %s is impressed with your progress on this goal: %s" \
                            % (tikedge_user.user.first_name, tikedge_user.user.last_name, progress_set.project.name_of_project)
            try:
                Notification.objects.get(user=progress_set.project.user.user, id_of_object=impressed_count.tasks.id)
            except ObjectDoesNotExist:
                impress_notif = Notification(user=progress_set.project.user.user, name_of_notification=name_of_notif,
                                         id_of_object=impressed_count.tasks.id,
                                         type_of_notification=global_variables.PROGRESS_WAS_IMPRESSED)
                impress_notif.save()
        response["count"] = impressed_count.get_count()
        return HttpResponse(json.dumps(response), status=201)


class ApiMilestoneView(CSRFExemptView):

    def get(self, request):
        response = {}
        try:
            username = request.GET.get("username")
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            response["status"] = False
            response["error"] = "Log back in and try again!"
            return HttpResponse(json.dumps(response), status=201)
        timezone = request.GET.get('timezone')
        mil_id = request.GET.get("mil_id")
        milestone = Milestone.objects.get(id=int(mil_id))
        project = milestone.project
        project_name = project.name_of_project
        feed_id = milestone.id
        modules.increment_milestone_view(user, milestone)
        try:
            vouch_count = VoucheMilestone.objects.get(tasks=milestone).users.count()
        except ObjectDoesNotExist:
            vouch_count = 0
        try:
            seen_count = SeenMilestone.objects.get(tasks=milestone).users.count()
            print "seen count ", seen_count
            print "seen count ", seen_count
        except ObjectDoesNotExist:
            seen_count = 0
        project_completed = task_modules.time_has_past(project.length_of_project, timezone=timezone)
        user_first_name = milestone.user.user.first_name
        pic_list = milestone.pictureset_set.all().filter(~Q(after_picture=None))
        percentage = modules.get_milestone_percentage(milestone)
        start_time = task_modules.utc_to_local(milestone.reminder, local_timezone=timezone).strftime("%B %d %Y %I:%M %p")
        end_time = task_modules.utc_to_local(milestone.done_by, local_timezone=timezone).strftime("%B %d %Y %I:%M %p")
        percent_sign = str(percentage) + "%"
        if milestone.is_active:
            percentage_statement = "Based on %s %s's community, there is a %s  chance of completing " \
                               "this milestone" % (user_first_name, milestone.user.user.last_name, percent_sign)
        else:
            percentage_statement = "Based on %s %s's community, there was a %s  chance of completing " \
                               "this milestone" % (user_first_name, milestone.user.user.last_name, percent_sign)
        if milestone.is_completed:
            is_completed = "Completed!"
        elif milestone.is_failed:
            is_completed = "Failed!"
        else:
            is_completed = None
        response = {
            'status':True,
            'project_completed': project_completed,
            'feed_id':feed_id,
            'project_name':project_name,
            'seen_count': seen_count,
            'pic_list':modules.get_pic_list(pic_list),
            'percentage_statement':percentage_statement,
            'end_time':end_time,
            'start_time':start_time,
            'project_id':project.id,
            'user_first_name':user_first_name,
            'user_last_name':milestone.user.user.last_name,
            'milestone_name':milestone.name_of_milestone,
            'vouch_count':vouch_count,
            'is_completed':is_completed,
            'user_id':milestone.user.user.id
        }

        return HttpResponse(json.dumps(response), status=201)


class ApiProjectView(CSRFExemptView):

    def get(self, request):
        response = {}
        try:
            username = request.GET.get("username")
            req_user = User.objects.get(username=username)
            proj_id = request.GET.get("proj_id")
        except ObjectDoesNotExist:
            response["status"] = False
            response["error"] = "Log back in and try again!"
            return HttpResponse(json.dumps(response), status=201)
        project = UserProject.objects.get(id=int(proj_id))
        project_name = project.name_of_project
        motivations = project.tags.all()
        print "motivations ", motivations
        modules.increment_project_view(req_user, project)
        milestones = project.milestone_set.all().filter(Q(is_deleted=False))
        try:
            seen_count = SeenProject.objects.get(tasks=project).get_count()
        except ObjectDoesNotExist:
            seen_count = 0
        try:
            follows = Follow.objects.get(tasks=project).users.count()
        except ObjectDoesNotExist:
            follows = 0
        user_owns_proj = TikedgeUser.objects.get(user=req_user) == project.user.user
        timezone_ = request.GET.get('timezone')
        progress = ProgressPictureSet.objects.get(project=project)

        public_status = "Project is in Pond"
        if project.is_public:
            public_status = "Project is Public"
        if project.is_completed:
            is_completed = "Completed!"
        elif project.is_failed:
            is_completed = "Failed!"
        else:
            is_completed = None
        response = {
            'status':True,
            'project_name':project_name,
            'user_first_name':project.user.user.first_name,
            'user_last_name':project.user.user.last_name,
            'start_time':task_modules.utc_to_local(project.made_live, local_timezone=timezone_).strftime("%B %d %Y %I:%M %p"),
            'end_time':task_modules.utc_to_local(project.length_of_project, local_timezone=timezone_).strftime("%B %d %Y %I:%M %p"),
            'seen_count':seen_count,
            'follow_count':follows,
            'public_status':public_status,
            'mil_list':modules.milestone_project_app_view(milestones),
            'motif':modules.motivation_for_project_app_view(motivations),
            'user_owns_proj':user_owns_proj,
            'is_completed':is_completed,
            'proj_id':project.id,
            'project_pic': task_modules.get_project_pic_info(project),
            'progresses': modules.get_picture_list_from_set(progress, timezone_=timezone_)
        }
        return HttpResponse(json.dumps(response), status=201)


class ApiProjectSeenCounter(CSRFExemptView):

    def post(self, request):
        response = {}
        try:
            username = request.POST.get("username")
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            response["status"] = False
            response["error"] = "Log back in and try again!"
            return HttpResponse(json.dumps(response), status=201)
        proj_id = request.POST.get("proj_id")
        try:
            project = UserProject.objects.get(id=int(proj_id))
            modules.increment_project_view(user, project)
        except (ObjectDoesNotExist, ValueError, AttributeError):
            pass
        response["status"] = True
        return HttpResponse(json.dumps(response), status=201)


class ApiMilestoneSeenCounter(CSRFExemptView):

    def post(self, request):
        response = {}
        try:
            username = request.POST.get("username")
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            response["status"] = False
            response["error"] = "Log back in and try again!"
            return HttpResponse(json.dumps(response), status=201)
        proj_id = request.POST.get("mil_id")
        try:
            milestone = Milestone.objects.get(id=int(proj_id))
            modules.increment_milestone_view(user, milestone)
        except (ObjectDoesNotExist, ValueError, AttributeError):
            pass
        response["status"] = True
        return HttpResponse(json.dumps(response), status=201)


class ApiGetPondList(CSRFExemptView):
    def get(self, request):
        response = {}
        try:
            username = request.GET.get("username")
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            response["status"] = False
            response["error"] = "Log back in and try again!"
            return HttpResponse(json.dumps(response), status=201)
        ponds = modules.get_pond(user)
        if ponds:
            pond_list = modules.pond_to_json(ponds)
            no_pond = False
        else:
            pond_list = modules.pond_to_json(Pond.objects.filter(is_deleted=False))
            no_pond = True

        response = {
            "status":True,
            "pond_list":pond_list,
            "no_pond":no_pond
        }
        return HttpResponse(json.dumps(response), status=201)


class ApiGetPond(CSRFExemptView):
    def get(self, request):
        """
        Get individual pond
        :param request:
        :return:
        """
        response = {}
        try:
            username = request.GET.get("username")
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            response["status"] = False
            response["error"] = "Log back in and try again!"
            return HttpResponse(json.dumps(response), status=201)
        pond_id = request.GET.get("pond_id")
        try:
            the_pond = Pond.objects.get(id=int(pond_id))
            pond_list_members = the_pond.pond_members.all()
            ponders = modules.get_pond_profile(pond_list_members, the_pond.pond_creator)
            tikedge_user = task_modules.get_tikedge_user(user)
            pond_member = pond_list_members.filter(user=tikedge_user.user)
            pond_tags = modules.get_tag_list(the_pond.tags.all())
            if pond_member:
                is_pond_member = True
            else:
                is_pond_member = False
            pond_status = task_modules.get_pond_status(pond_list_members)
            response["status"] = True
            response["pond_info"] = {
                "ponders":ponders,
                "pond_status":pond_status,
                "purpose":the_pond.purpose,
                "name_of_pond":the_pond.name_of_pond,
                "is_member":is_pond_member,
                "tags":pond_tags,
                'id':int(pond_id)
            }
        except ObjectDoesNotExist:
            response["status"] = False
            response["error"] = "Something went wrong refresh the page!"
        return HttpResponse(json.dumps(response), status=201)


class ApiPondRequestView(CSRFExemptView):
    """
        Send Pond Request to pond members
    """
    def post(self, request):
        response = {}
        try:
            username = request.POST.get("username")
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            response["status"] = False
            response["error"] = "Log back in and try again!"
            return HttpResponse(json.dumps(response), status=201)
        try:
            pond_id = request.POST.get("pond_id")
            pond = Pond.objects.get(id=int(pond_id))
            response = modules.send_pond_request(pond, user)
        except ObjectDoesNotExist:
            pass
        return HttpResponse(json.dumps(response))


class ApiGetSearchResult(CSRFExemptView):
    """
        Api Call for Search Result
    """

    def get(self, request):
        response = {}
        try:
            username = request.GET.get("username")
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            response["status"] = False
            response["error"] = "Log back in and try again!"
            return HttpResponse(json.dumps(response), status=201)
        query_word = request.GET["query_word"]
        results = find_everything(user, query_word)
        response["status"] = True
        print type(results)
        response["result_list"] = search_result_jsonified(results)
        return HttpResponse(json.dumps(response))


class ApiAddToPond(CSRFExemptView):

    def post(self, request):
        response = {}
        try:
            username = request.POST.get("username")
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            response["status"] = False
            response["error"] = "Log back in and try again!"
            return HttpResponse(json.dumps(response), status=201)
        data = {}
        pond_id = request.POST.get("pond_id")
        pond = Pond.objects.get(id=int(pond_id))
        user_id = request.POST.get("user_id")
        other_user = TikedgeUser.objects.get(id=int(user_id))
        try:
            PondMembership.objects.get(user=other_user, pond=pond, date_removed=None)
            response['status'] = True
            return HttpResponse(json.dumps(data))
        except ObjectDoesNotExist:
            pass
        try:
            pond_members = pond.pond_members.all()
            if other_user not in pond_members:
                pond_mess = "%s %s has been added to your pond: %s" % (other_user.user.first_name,
                                                                       other_user.user.last_name, pond.name_of_pond)
                for each_member in pond_members:
                    notification = Notification(user=each_member.user, name_of_notification=pond_mess, id_of_object=pond.id,
                                            type_of_notification=global_variables.NEW_PONDERS)
                    notification.save()
                pond.pond_members.add(other_user)
                pond.save()
                pond_membership = PondMembership(user=other_user, pond=pond)
                pond_membership.save()

                try:
                    pond_request_already_exist = PondRequest.objects.get(pond=pond, user=other_user, request_responded_to=False)
                    pond_request_already_exist.request_responded_to = True
                    pond_request_already_exist.date_response=timezone.now()
                    pond_request_already_exist.request_accepted = True
                    pond_request_already_exist.member_that_responded=task_modules.get_tikedge_user(user)
                    pond_request_already_exist.save()
                    req_id = pond_request_already_exist.id
                except ObjectDoesNotExist:
                    pond_request = PondRequest(user=other_user, pond=pond, date_response=timezone.now(),
                                               request_accepted=True,
                                               member_that_responded=task_modules.get_tikedge_user(user),
                                               request_responded_to=True)
                    pond_request.save()
                    req_id = pond_request.id
                pond_mess = "Congratulations! You have been added to this pond: %s." % pond.name_of_pond
                notification = Notification(user=other_user.user, name_of_notification=pond_mess, id_of_object=req_id,
                                            type_of_notification=global_variables.POND_REQUEST_ACCEPTED)
                notification.save()
            else:
                print "others is here!!!!!!!!!"
            data['status'] = True
            aval_pond = modules.available_ponds_json(other_user, user)
            data['aval_pond'] = aval_pond
        except (AttributeError, ValueError, TypeError):
            data['status'] = False
            data['error'] = "Something Went Wrong, Try Again!"
            pass
        return HttpResponse(json.dumps(data))


class ApiDenyPondRequest(CSRFExemptView):

    def post(self, request):
        response = {}
        try:
            username = request.POST.get("username")
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            response["status"] = False
            response["error"] = "Log back in and try again!"
            return HttpResponse(json.dumps(response), status=201)
        data = {}
        pond_request_id = request.POST.get("pond_request_id")
        pond_request = PondRequest.objects.get(id=int(pond_request_id))
        if pond_request.request_responded_to or pond_request.pond.is_deleted:
            data["status"] = True
            return HttpResponse(json.dumps(data))
        else:
            try:
                pond_request.date_response = timezone.now()
                pond_request.request_accepted = False
                pond_request.request_denied = True
                pond_request.request_responded_to = True
                pond_request.member_that_responded = task_modules.get_tikedge_user(user)
                pond_request.save()
                data["status"] = True
                return  HttpResponse(json.dumps(data))
            except (AttributeError, ValueError, TypeError, Exception):
                data["status"] = False
                data["error"] = "An error occurred try again! Also the user might have already been removed"
                return HttpResponse(json.dumps(data))


class ApiNotificationView(CSRFExemptView):

    def get(self, request):
        response = {}
        try:
            username = request.GET.get("username")
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            response["status"] = False
            response["error"] = "Log back in and try again!"
            return HttpResponse(json.dumps(response), status=201)
        timezone = request.GET.get('timezone')
        notification_list = modules.get_notification_of_user(user, timezone=timezone)
        response['status'] = True
        response['notification_list'] = notification_list
        modules.mark_new_ponder_notification_as_read(user)
        modules.mark_new_project_interested_as_read(user)
        modules.mark_project_viewed(user)
        modules.mark_progress_impressed_as_read(user)
        modules.mark_goal_let_down_as_read(user)
        modules.mark_pond_request_notification_as_read(user)
        modules.mark_milestone_pond_request_accepted_as_read(user)
        modules.mark_project_failed_as_read(user)
        modules.mark_new_progress_added_as_read(user)
        modules.mark_new_project_added_as_read(user)
        return HttpResponse(json.dumps(response))


class ApiAcceptPondRequest(CSRFExemptView):

    def post(self, request):
        data = {}
        try:
            username = request.POST.get("username")
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            data["status"] = False
            data["error"] = "Log back in and try again!"
            return HttpResponse(json.dumps(data), status=201)
        pond_request_id = request.POST.get("pond_request_id")
        pond_request = PondRequest.objects.get(id=int(pond_request_id))
        if pond_request.request_responded_to or pond_request.pond.is_deleted:
            if pond_request.pond.is_deleted:
                pond_request.date_response = timezone.now()
                pond_request.request_accepted = False
                pond_request.request_denied = True
                pond_request.request_responded_to = True
                pond_request.member_that_responded = task_modules.get_tikedge_user(user)
                pond_request.save()
            data["status"] = True
            return HttpResponse(json.dumps(data))
        else:
            try:
                pond_request.date_response = timezone.now()
                pond_request.request_accepted = True
                pond_request.request_responded_to = True
                pond_request.member_that_responded = task_modules.get_tikedge_user(user)
                pond_request.save()
                data["status"] = True
                pond_mess = "Request granted to join pond: %s!" %  pond_request.pond.name_of_pond
                new_notif = Notification(user=pond_request.user.user, name_of_notitification=pond_mess,
                                         id_of_object=pond_request.id,
                                         type_of_notification=global_variables.POND_REQUEST_ACCEPTED)
                new_notif.save()
                for each_member in pond_request.pond.pond_members.all():
                    pond_mess = "Pond: %s has new member: %s %s" % (pond_request.pond.name_of_pond,
                                                                    each_member.user.first_name, each_member.user.last_name)
                    new_notif = Notification(user=each_member.user, name_of_notification=pond_mess, id_of_object=pond_request.id,
                                             type_of_notification=global_variables.NEW_PONDERS)
                    new_notif.save()
                pond_request.pond.pond_members.add(pond_request.user)
                pond_request.pond.save()
                pond_membership = PondMembership(user=pond_request.user, pond=pond_request.pond)
                pond_membership.save()
                return  HttpResponse(json.dumps(data))
            except (AttributeError, ValueError, TypeError, Exception):
                data["status"] = False
                data["error"] = "An error occurred. Please try again! Also pond request might have already been accepted!"
                return HttpResponse(json.dumps(data))


class ApiGetNotification(CSRFExemptView):

    def get(self, request):
        data = {}
        try:
            username = request.GET.get("username")
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            data["status"] = False
            data["error"] = "Log back in and try again!"
            return HttpResponse(json.dumps(data), status=201)
        data = {}
        data["data"] = modules.notification_exist(user)
        return HttpResponse(json.dumps(data))