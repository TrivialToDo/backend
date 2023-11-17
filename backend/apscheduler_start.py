from apscheduler.schedulers.background import BackgroundScheduler
from wechat.utils import send_message
from user.models import User
from utils.utils_logger import get_logger


def my_job():
    logger = get_logger()
    send_message(User(wechat_id='wxid_s1epg7j4rred22'), 'test', "fuck you")
    logger.info("request wx")


scheduler = BackgroundScheduler()
job = scheduler.add_job(my_job, timezone='Asia/Shanghai', trigger='interval', seconds=10)
get_logger().info(job.id)
scheduler.start()

try:
    import uwsgi

    while True:
        sig = uwsgi.signal_wait()
except Exception as err:
    pass
