import datetime
from wechat.utils import send_message
from user.models import User
from utils.utils_logger import get_logger
from utils.utils_scheduler import get_scheduler
from event.models import Event
from wechat.views import process_room_msgs


def my_job():
    logger = get_logger()
    print("Abc")
    logger.info("request wx")


scheduler = get_scheduler()
# job = scheduler.add_job(my_job, timezone='Asia/Shanghai', trigger='interval', seconds=10)
# get_logger().info(job.id)
job = scheduler.add_job(process_room_msgs, timezone='Asia/Shanghai', trigger='interval', seconds=300)
get_logger().info(job.id)
events = Event.objects.filter(dateEnd__gt=datetime.datetime.now(), repeat__in=['daily', 'weekly', 'monthly']).all()
events |= Event.objects.filter(dateStart__gt=datetime.datetime.now(), repeat='never').all()
for event in events:
    event.add_schedule_reminder()
if scheduler.state == 0:
    scheduler.start()

try:
    import uwsgi

    while True:
        sig = uwsgi.signal_wait()
except Exception as err:
    pass
