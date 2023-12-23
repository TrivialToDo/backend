import hashlib
import json
from datetime import date, time, datetime

from django.db import models
from django.http import JsonResponse
from user.models import User
from typing import Optional, Dict
from utils.utils_scheduler import get_scheduler
from wechat.utils import send_message


# Create your models here.

class Event(models.Model):
    hash = models.CharField(max_length=32, primary_key=True)
    title = models.CharField(max_length=100, default='Untitled')
    description = models.TextField(default='')
    repeat = models.CharField(max_length=10, default='never', choices=(
        ('never', 'Never'), ('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')
    ))
    timeStart = models.TimeField(null=False)
    timeEnd = models.TimeField(null=True)
    dateStart = models.DateField(null=False)
    dateEnd = models.DateField(default=date(9999, 12, 31))
    dayOfWeek = models.IntegerField(null=True)  # 0-6
    dayOfMonth = models.IntegerField(null=True)  # 1-31
    reminder = models.TimeField(null=True)
    remind_type = models.CharField(max_length=10, default='wechat', choices=(
        ('message', 'Message'), ('phone_call', 'Phone Call'), ('wechat', 'WeChat')
    ))

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def serialize(self):
        res = {
            'hash': self.hash,
            'title': self.title,
            'description': self.description,
            'repeat': self.repeat,
            'timeStart': {
                'hour': self.timeStart.hour,
                'minute': self.timeStart.minute,
            },
            'dateStart': self.dateStart.isoformat(),
        }
        if self.timeEnd:
            res['timeEnd'] = {
                'hour': self.timeEnd.hour,
                'minute': self.timeEnd.minute,
            }
        if self.dateEnd:
            res['dateEnd'] = self.dateEnd.isoformat()
        if self.reminder:
            res['reminder'] = {
                'hour': self.reminder.hour,
                'minute': self.reminder.minute,
            }

        return res

    def add_schedule_reminder(self):
        if self.reminder is None:
            return
        scheduler = get_scheduler()
        start_date = self.dateStart

        def remind_func(remind_type):
            # TODO: send remind
            if remind_type == 'wechat':
                send_message(self.user, 'text', "❗❗❗" + '\n' + self.title + '\n' + self.description)
            elif remind_type == 'message':
                pass
            elif remind_type == 'phone_call':
                pass

        if self.repeat == 'never':
            scheduler.add_job(
                lambda: remind_func(self.remind_type),
                'date',
                id=self.hash,
                run_date=datetime.combine(start_date, self.reminder),
                replace_existing=True
            )
            return
        end_date = self.dateEnd
        if self.repeat == 'daily':
            scheduler.add_job(
                lambda: remind_func(self.remind_type),
                'cron',
                id=self.hash,
                start_date=datetime.combine(start_date, self.reminder),
                end_date=datetime.combine(end_date, self.reminder),
                day='*',
                replace_existing=True
            )
        elif self.repeat == 'weekly':
            scheduler.add_job(
                lambda: remind_func(self.remind_type),
                'cron',
                id=self.hash,
                start_date=datetime.combine(start_date, self.reminder),
                end_date=datetime.combine(end_date, self.reminder),
                day_of_week=self.dayOfWeek,
                replace_existing=True
            )
        elif self.repeat == 'monthly':
            scheduler.add_job(
                lambda: remind_func(self.remind_type),
                'cron',
                id=self.hash,
                start_date=datetime.combine(start_date, self.reminder),
                end_date=datetime.combine(end_date, self.reminder),
                day=self.dayOfMonth,
                replace_existing=True
            )

    @staticmethod
    def create_event(
            user: User,
            time_start: Dict[str, int],
            date_start: str,
            time_end: Optional[Dict[str, int]] = None,
            date_end: Optional[str] = None,
            title: str = 'Untitled',
            description: str = '',
            repeat: str = 'never',
            reminder: Optional[Dict[str, int]] = None
    ):
        if title is None:
            title = 'Untitled'
        if description is None:
            description = ''

        _hash = hashlib.md5(
            (
                    title + ';' +
                    description + ';' +
                    repeat + ';' +
                    str(time_start) + ';' +
                    str(time_end) + ';' +
                    str(date_start) + ';' +
                    str(date_end) + ';' +
                    json.dumps(user.serialize())
            ).encode('utf-8')
        ).hexdigest()

        time_start = time(hour=time_start['hour'], minute=time_start['minute'])
        time_end = time(hour=time_end['hour'], minute=time_end['minute']) if time_end is not None else None
        date_start = datetime.fromisoformat(date_start).date()
        date_end = datetime.fromisoformat(date_end).date() if date_end is not None else date(9999, 12, 31)
        reminder = time(hour=reminder['hour'], minute=reminder['minute']) if reminder is not None else None

        if repeat not in ['never', 'daily', 'weekly', 'monthly']:
            return None, JsonResponse({
                "code": 400,
                "data": {
                    "msg": f"invalid repeat: {repeat}"
                }
            }, status=400)
        if time_end is not None and time_start > time_end:
            return None, JsonResponse({
                "code": 400,
                "data": {
                    "msg": f"invalid time range: {time_start} > {time_end}"
                }
            }, status=400)
        if date_start > date_end:
            return None, JsonResponse({
                "code": 400,
                "data": {
                    "msg": f"invalid date range: {date_start} > {date_end}"
                }
            }, status=400)
        if reminder is not None and time_start < reminder:
            return None, JsonResponse({
                "code": 400,
                "data": {
                    "msg": f"invalid reminder: {new_time_start} < {new_reminder}"
                }
            }, status=400)

        e = Event(
            hash=_hash,
            title=title,
            description=description,
            repeat=repeat,
            timeStart=time_start,
            timeEnd=time_end,
            dateStart=date_start,
            dateEnd=date_end,
            reminder=reminder,
            user=user
        )
        if repeat == 'weekly':
            e.dayOfWeek = date_start.weekday()
        elif repeat == 'monthly':
            e.dayOfMonth = date_start.day
        e.add_schedule_reminder()
        e.save()
        return e, None

    @staticmethod
    def modify_event(
            user: User,
            hash: str,
            time_start: Dict[str, int] = None,
            date_start: str = None,
            time_end: Optional[Dict[str, int]] = None,
            date_end: Optional[str] = None,
            title: str = None,
            description: str = None,
            repeat: str = None,
            reminder: Optional[Dict[str, int]] = None
    ):
        try:
            event = Event.objects.get(hash=hash)
        except Event.DoesNotExist:
            event = None
        if not event:
            return None, JsonResponse({
                "code": 404,
                "data": {
                    "msg": f"event with hash {hash} not found"
                }
            }, status=404)
        if event.user != user:
            return None, JsonResponse({
                "code": 403,
                "data": {
                    "msg": f"event with hash {hash} not belong to user {user.wechat_id}"
                }
            }, status=403)

        new_time_start = time(hour=time_start['hour'], minute=time_start['minute']) if time_start is not None else None
        new_time_end = time(hour=time_end['hour'], minute=time_end['minute']) if time_end is not None else None
        new_date_start = datetime.fromisoformat(date_start).date() if date_start is not None else None
        new_date_end = datetime.fromisoformat(date_end).date() if date_end is not None else None
        new_reminder = time(hour=reminder['hour'], minute=reminder['minute']) if reminder is not None else None

        if repeat not in ['never', 'daily', 'weekly', 'monthly']:
            return None, JsonResponse({
                "code": 400,
                "data": {
                    "msg": f"invalid repeat: {repeat}"
                }
            }, status=400)
        if new_time_end is not None and new_time_start > new_time_end:
            return None, JsonResponse({
                "code": 400,
                "data": {
                    "msg": f"invalid time range: {new_time_start} > {new_time_end}"
                }
            }, status=400)
        if new_date_start > new_date_end:
            return None, JsonResponse({
                "code": 400,
                "data": {
                    "msg": f"invalid date range: {new_date_start} > {new_date_end}"
                }
            }, status=400)
        if new_reminder is not None and new_time_start < new_reminder:
            return None, JsonResponse({
                "code": 400,
                "data": {
                    "msg": f"invalid reminder: {time_start} < {reminder}"
                }
            }, status=400)

        if title is not None:
            event.title = title
        if description is not None:
            event.description = description
        if repeat is not None:
            event.repeat = repeat
            if repeat == 'weekly':
                event.dayOfWeek = new_date_start.weekday()
                event.dayOfMonth = None
            elif repeat == 'monthly':
                event.dayOfWeek = None
                event.dayOfMonth = new_date_start.day
            else:
                event.dayOfWeek = None
                event.dayOfMonth = None
        if new_time_start is not None:
            event.timeStart = new_time_start
        if new_time_end is not None:
            event.timeEnd = new_time_end
        if new_date_start is not None:
            event.dateStart = new_date_start
        if new_date_end is not None:
            event.dateEnd = new_date_end
        if new_reminder is not None:
            event.reminder = new_reminder

        event.save()
        return event, None

    @staticmethod
    def remove_all_events(user: User):
        Event.objects.filter(user=user).delete()
