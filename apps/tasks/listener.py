from django.db.models.signals import post_save
from tasks.models import Tasks
from tasks.tasks import print_reminder


def reminder_handler(*args, **kwargs):
    print_reminder.apply_async(eta=instance.start, kwargs={'pk': instance.pk})

post_save.connect(reminder_handler, sender=Tasks)