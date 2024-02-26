from apscheduler.schedulers.background import BackgroundScheduler

from utils.utils_logger import get_logger

scheduler = BackgroundScheduler()


def get_scheduler():
    return scheduler


def add_reminder(text):
    def my_job():
        get_logger().info(text)
    scheduler.add_job(
        my_job,
        trigger='interval',
        timezone='Asia/Shanghai',
        seconds=10,
        id='test',
        replace_existing=True
    )
    scheduler.start()
