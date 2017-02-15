import pytz
from datetime import datetime

def get_current_datetime():
    local = datetime.now(pytz.utc)
    return local