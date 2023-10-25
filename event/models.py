import hashlib
from datetime import date, time, datetime

from django.db import models
from django.http import JsonResponse


# Create your models here.

class Event(models.Model):
    hash = models.CharField(max_length=32, primary_key=True)
    title = models.CharField(max_length=100, default='Untitled')
    description = models.TextField(default='')
    repeat = models.CharField(max_length=10, default='never', choices=(
        ('never', 'Never'), ('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')))
    timeStart = models.TimeField(null=False)
    timeEnd = models.TimeField(null=True)
    dateStart = models.DateField(null=False)
    dateEnd = models.DateField(default=date(9999, 12, 31))
    dayOfWeek = models.IntegerField(null=True)  # 0-6
    dayOfMonth = models.IntegerField(null=True)  # 1-31

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

        return res

    @staticmethod
    def create_event(time_start: dict, date_start: str, time_end: dict = None, date_end: str = None,
                     title: str = 'Untitled', description: str = '', repeat: str = 'never'):
        _hash = hashlib.md5(
            (title + ';' + description + ';' + repeat + ';' +
             str(time_start) + ';' + str(time_end) + ';' + date_start + ';' + str(date_end)).encode('utf-8')
        ).hexdigest()
        time_start = time(hour=time_start['hour'], minute=time_start['minute'])
        time_end = time(hour=time_end['hour'], minute=time_end['minute']) if time_end is not None else None
        date_start = datetime.fromisoformat(date_start).date()
        date_end = datetime.fromisoformat(date_end).date() if date_end is not None else date(9999, 12, 31)

        if repeat not in ['never', 'daily', 'weekly', 'monthly']:
            return None, JsonResponse({
                "code": 400,
                "data": {
                    "msg": "invalid repeat"
                }
            }, status=400)

        if time_end is not None and time_start > time_end:
            return None, JsonResponse({
                "code": 400,
                "data": {
                    "msg": "invalid time range"
                }
            }, status=400)
        if date_start > date_end:
            return None, JsonResponse({
                "code": 400,
                "data": {
                    "msg": "invalid date range"
                }
            }, status=400)

        e = Event(hash=_hash, title=title, description=description, repeat=repeat,
                  timeStart=time_start, timeEnd=time_end, dateStart=date_start, dateEnd=date_end)
        if repeat == 'weekly':
            e.dayOfWeek = date_start.weekday()
        elif repeat == 'monthly':
            e.dayOfMonth = date_start.day
        e.save()
        return e, None
