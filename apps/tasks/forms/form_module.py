from tzlocal import get_localzone
from django.utils import timezone
from datetime import datetime


def get_current_datetime():
    local = timezone.now()
    print "current time", local,
    return local