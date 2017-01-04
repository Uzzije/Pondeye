import global_variables
import re
from django.db.models import Q
from ..tasks.models import TikedgeUser, Milestone, UserProject
from models import User
from .models import ProfilePictures, Pond, PondSpecificProject
from django.core.exceptions import ObjectDoesNotExist


class GeneralSearchFeed:
	def __init__(self, return_object, type_of_result):
		self.feed_object = return_object
		self.type_of_result = type_of_result
		self.is_person = self.get_is_person()
		self.is_project = self.get_is_project()
		self.is_milestone = self.get_is_milestone()
		self.is_pond = self.get_is_pond()
		self.created = self.date_created()

	def get_is_person(self):
		if self.type_of_result == global_variables.PERSON_SEARCH:
			print "feed object ", type(self.feed_object)
			tikedge_user = TikedgeUser.objects.get(user=self.feed_object)
			try:
				profile_pic = ProfilePictures.objects.get(tikedge_user=tikedge_user)
			except ObjectDoesNotExist:
				profile_pic = "no picture"
			return profile_pic
		else:
			return False

	def get_is_project(self):
		if (self.type_of_result == global_variables.PROJECT_NAME_SEARCH):
			return True
		else:
			return False

	def get_is_milestone(self):
		if self.type_of_result == global_variables.MILESTONE_NAME_SEARCH:
			return True
		else:
			return False

	def date_created(self):
		if self.type_of_result == global_variables.PERSON_SEARCH:
			date_created = self.feed_object.date_joined
		elif (self.type_of_result == global_variables.PROJECT_NAME_SEARCH):
			date_created = self.feed_object.made_live
		elif self.type_of_result == global_variables.POND_SEARCH_NAME:
			date_created = self.feed_object.date_created
		else:
			date_created = self.feed_object.created_date
		return date_created

	def get_is_pond(self):
		if self.type_of_result == global_variables.POND_SEARCH_NAME:
			return True
		else:
			return False


def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:

        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']

    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]


def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.

    '''
    query = None # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        print term
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query


def find_everything(user, query_word):
	result_list = []
	query = str(query_word)
	people = get_query(query, ['username', 'first_name', 'last_name'])
	people_result = User.objects.filter(people).filter(~Q(username=user.username),
	                                                   (Q(is_staff=False) | Q(is_superuser=False))).distinct()
	projects = get_query(query, ['name_of_project', 'tags__name_of_tag'])
	print query, " projddd"
	tikege_user = TikedgeUser.objects.get(user=user)
	projects_result = UserProject.objects.filter(projects).filter(Q(is_deleted=False)).distinct()
	milestones = get_query(query, ['name_of_milestone'])
	milestones_result = Milestone.objects.filter(milestones).filter(Q(is_deleted=False)).distinct()
	ponds = get_query(query, ['name_of_pond', 'tags__name_of_tag', 'purpose'])
	pond_list = Pond.objects.filter(ponds).filter(Q(is_deleted=False)).distinct()
	print "project %s \n" % projects_result

	for pip in people_result:
		search_obj = GeneralSearchFeed(pip, global_variables.PERSON_SEARCH)
		result_list.append(search_obj)
	for proj in projects_result:

		if not proj.is_public:
			pond_spec = PondSpecificProject.objects.get(project=proj)
			for each_pond in pond_spec.pond.all():
				if tikege_user in each_pond.pond_members.all():
					search_obj = GeneralSearchFeed(proj, global_variables.PROJECT_NAME_SEARCH)
					result_list.append(search_obj)
					break
		else:
			search_obj = GeneralSearchFeed(proj, global_variables.PROJECT_NAME_SEARCH)
			result_list.append(search_obj)
	for mil in milestones_result:
		if not mil.project.is_public:
			pond_spec = PondSpecificProject.objects.get(project=mil.project)
			for each_pond in pond_spec.pond.all():
				if tikege_user in each_pond.pond_members.all():
					search_obj = GeneralSearchFeed(mil, global_variables.MILESTONE_NAME_SEARCH)
					result_list.append(search_obj)
					break
		else:
			search_obj = GeneralSearchFeed(mil, global_variables.MILESTONE_NAME_SEARCH)
			result_list.append(search_obj)
	for pond in pond_list:
		search_obj = GeneralSearchFeed(pond, global_variables.POND_SEARCH_NAME)
		result_list.append(search_obj)
	print result_list
	sorted_list = sorted(result_list, key=lambda res: res.created)
	return sorted_list


def find_project_and_milestone_by_tag(user, query_word):
	result_list = []
	query = str(query_word)
	projects = get_query(query, ['name_of_project', 'tags__name_of_tag'])
	projects_result = UserProject.objects.filter(Q(is_public=True),Q(is_deleted=False)).filter(projects)
	milestones = get_query(query, ['name_of_milestone'])
	milestones_result = Milestone.objects.filter(milestones).filter(Q(project__is_public=True), Q(is_deleted=False))
	user_ponds = Pond.objects.filter(Q(pond_members__user=user), Q(is_deleted=False))
	pond_specific_query = get_query(query, ['project__name_of_project', 'project__tags__name_of_tag'])
	pond_specific_result = PondSpecificProject.objects.filter(pond__in=user_ponds).filter(pond_specific_query)

	for proj in projects_result:
		search_obj = GeneralSearchFeed(proj, global_variables.PROJECT_NAME_SEARCH)
		result_list.append(search_obj)
	for mil in milestones_result:
		search_obj = GeneralSearchFeed(mil, global_variables.MILESTONE_NAME_SEARCH)
		result_list.append(search_obj)
	for each_spec in pond_specific_result:
		search_obj = GeneralSearchFeed(each_spec.project, global_variables.PROJECT_NAME_SEARCH)
		result_list.append(search_obj)
		private_milestone = each_spec.project.milestone_set.filter(milestones)
		for each_priv_mil in private_milestone:
			search_obj = GeneralSearchFeed(each_priv_mil, global_variables.MILESTONE_NAME_SEARCH)
			result_list.append(search_obj)
	print result_list
	sorted_list = sorted(result_list, key=lambda res: res.created)
	return sorted_list
