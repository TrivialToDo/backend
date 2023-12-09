import datetime
from wechat.utils import send_message
from user.models import User
from utils.utils_logger import get_logger
from utils.utils_scheduler import get_scheduler
from event.models import Event

def my_job():
    logger = get_logger()
    send_message(User(wechat_id='wxid_s1epg7j4rred22'), 'text', "fuck you")
    logger.info("request wx")


scheduler = get_scheduler()
events = Event.objects.filter(dateEnd__gt=datetime.datetime.now(), repeat__in=['daily', 'weekly', 'monthly']).all()
events |= Event.objects.filter(dateStart__gt=datetime.datetime.now(), repeat='never').all()
for event in events:
    event.add_schedule_reminder()
scheduler.start()

try:
    import uwsgi

    while True:
        sig = uwsgi.signal_wait()
except Exception as err:
    pass
