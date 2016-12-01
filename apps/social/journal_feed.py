import global_variables
from ..tasks.modules import utc_to_local


class JournalFeed:
	def __init__(self, journal):
		self.feed_entry = journal
		self.entry = journal.entry_blurb
		self.day_entry = journal.day_entry
		self.day_created = journal.day_created.strftime("%B %d %Y %I:%M %p")
		self.is_pic_set = journal.is_picture_set
		self.is_mil = journal.is_milestone_entry
		self.is_proj = journal.is_project_entry
		self.comment_id = journal.id
		self.content = self.get_content()

	def get_content(self):
		if self.is_mil:
			return self.feed_entry.milestone_entry
		if self.is_pic_set:
			return self.feed_entry.picture_set_entry
		if self.is_proj:
			return self.feed_entry.new_project_entry
		return None


