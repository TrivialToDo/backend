from datetime import datetime, timedelta

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from event.models import Event


# Create your views here.

def get_day_event(_date: datetime.date):
    r = Event.objects.filter(repeat='never', dateStart=_date).all() | \
        Event.objects.filter(repeat='daily', dateStart__lte=_date, dateEnd__gte=_date).all() | \
        Event.objects.filter(repeat='monthly', dateStart__lte=_date, dateEnd__gte=_date, dayOfMonth=_date.day).all() | \
        Event.objects.filter(repeat='weekly', dateStart__lte=_date, dateEnd__gte=_date, dayOfWeek=_date.weekday()).all()
    r = r.order_by('timeStart')
    return r


def get_date(request, _date: str):
    try:
        _date = datetime.strptime(_date, '%Y-%m-%d').date()
    except ValueError:
        return None, JsonResponse({
            "code": 400,
            "data": {
                "msg": "invalid date format"
            }
        }, status=400)

    return _date, None


@require_http_methods(['GET'])
def get_day(request, _date: str):
    _date, err = get_date(request, _date)
    if err:
        return err

    r = get_day_event(_date)
    return JsonResponse({
        "code": 200,
        "data": {
            "list": [i.serialize() for i in r]
        }
    })


@require_http_methods(['GET'])
def get_week(request, _date: str):
    _date, err = get_date(request, _date)
    if err:
        return err

    r = []
    for _ in range(7):
        r.append([i.serialize() for i in get_day_event(_date)])
        _date = _date + timedelta(days=1)
    return JsonResponse({
        "code": 200,
        "data": {
            "list": r
        }
    })


@require_http_methods(['GET'])
def get_month(request, _date: str):
    _date, err = get_date(request, _date)
    if err:
        return err

    r = []
    for _ in range(31):
        r.append([i.serialize() for i in get_day_event(_date)])
        _date = _date + timedelta(days=1)
        if _date.day == 1:
            break
    return JsonResponse({
        "code": 200,
        "data": {
            "list": r
        }
    })
