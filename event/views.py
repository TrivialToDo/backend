import json

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from utils.utils_login import login_check
from utils.utils_request import request_success, request_fail
from .models import Event
from user.models import User


# Create your views here.


@login_check
@require_http_methods(["GET", "DELETE"])
def deal_event(request, hash: str, user: User = None):
    if request.method == "GET":
        return get_event(request, hash, user)
    elif request.method == "DELETE":
        return del_event(request, hash, user)


def get_event(request, hash: str, user: User = None):
    res = Event.objects.filter(hash=hash, user=user).first()
    if res is None:
        return request_fail(404, "event not found")
    return request_success({"event": res.serialize()})


def del_event(request, hash: str, user: User = None):
    res = Event.objects.filter(hash=hash, user=user).first()
    if res is None:
        return request_fail(404, "event not found")
    res.delete()
    return request_success({"msg": "Succeed"})


@login_check
@require_http_methods(["POST"])
def new_event(request, user: User = None):
    body = json.loads(request.body.decode('utf-8'))
    event = body.get("event")
    if event is None:
        return request_fail(400, "event not found")
    event, err = Event.create_event(
        user=user,
        time_start=event.get("timeStart"),
        date_start=event.get("dateStart"),
        time_end=event.get("timeEnd"),
        date_end=event.get("dateEnd"),
        title=event.get("title"),
        description=event.get("description"),
        repeat=event.get("repeat"),
        reminder=event.get("reminder"),
    )
    if err is not None:
        return err
    return request_success({"hash": event.hash})


@login_check
@require_http_methods(["POST"])
def modify_event(request, user: User = None):
    body = json.loads(request.body.decode('utf-8'))
    event = body.get("event")
    hash_ = body.get("hash")
    if event is None or hash_ is None:
        return request_fail(400, "event not found")
    event, err = Event.modify_event(
        user=user,
        hash=hash_,
        time_start=event.get("timeStart"),
        date_start=event.get("dateStart"),
        time_end=event.get("timeEnd"),
        date_end=event.get("dateEnd"),
        title=event.get("title"),
        description=event.get("description"),
        repeat=event.get("repeat"),
        reminder=event.get("reminder"),
    )
    if err is not None:
        return err
    return request_success({"hash": event.hash})
