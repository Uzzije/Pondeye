from tzlocal import get_localzone
from django.utils import timezone


def get_current_datetime():
    local = timezone.localtime(timezone.now())
    print "%s local time" % local
    return local