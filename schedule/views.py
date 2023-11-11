from datetime import datetime, timedelta
from user.models import User
from django.views.decorators.http import require_http_methods
from event.models import Event
from utils.utils_login import login_check
from utils.utils_request import request_success, request_fail


# Create your views here.

def get_day_event(_date: datetime.date, user: User = None):
    r = Event.objects.filter(
        user=user, repeat='never', dateStart=_date
    ).all()
    r = Event.objects.filter(
        user=user, repeat='daily', dateStart__lte=_date, dateEnd__gte=_date
    ).all() | r
    r = Event.objects.filter(
        user=user, repeat='monthly', dateStart__lte=_date, dateEnd__gte=_date, dayOfMonth=_date.day
    ).all() | r
    r = Event.objects.filter(
        user=user, repeat='weekly', dateStart__lte=_date, dateEnd__gte=_date, dayOfWeek=_date.weekday()
    ).all() | r
    r = r.order_by('timeStart')
    return r


def get_date(request, _date: str):
    try:
        _date = datetime.strptime(_date, '%Y-%m-%d').date()
    except ValueError:
        return None, request_fail(400, "invalid date format")

    return _date, None


@login_check
@require_http_methods(['GET'])
def get_day(request, _date: str, user: User = None):
    _date, err = get_date(request, _date)
    if err:
        return err

    r = get_day_event(_date, user)
    return request_success({
        "list": [[i.serialize() for i in r]]
    })


@login_check
@require_http_methods(['GET'])
def get_week(request, _date: str, user: User = None):
    _date, err = get_date(request, _date)
    if err:
        return err

    r = []
    for _ in range(7):
        r.append([i.serialize() for i in get_day_event(_date, user)])
        _date = _date + timedelta(days=1)
    return request_success({
        "list": r
    })


@login_check
@require_http_methods(['GET'])
def get_month(request, _date: str, user: User = None):
    _date, err = get_date(request, _date)
    if err:
        return err

    r = []
    for _ in range(31):
        r.append([i.serialize() for i in get_day_event(_date, user)])
        _date = _date + timedelta(days=1)
        if _date.day == 1:
            break
    return request_success({
        "list": r
    })
