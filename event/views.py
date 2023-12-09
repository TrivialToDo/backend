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
    event, response = Event.create_event(
        user=user,
        time_start=request.POST.get("timeStart"),
        date_start=request.POST.get("dateStart"),
        time_end=request.POST.get("timeEnd"),
        date_end=request.POST.get("dateEnd"),
        title=request.POST.get("title"),
        description=request.POST.get("description"),
        repeat=request.POST.get("repeat"),
        reminder=request.POST.get("reminder"),
    )
    if response is not None:
        return response
    return request_success({"hash": event.hash})


@login_check
@require_http_methods(["POST"])
def modify_event(request, user: User = None):
    event, response = Event.modify_event(
        user=user,
        hash=request.POST.get("hash"),
        time_start=request.POST.get("timeStart"),
        date_start=request.POST.get("dateStart"),
        time_end=request.POST.get("timeEnd"),
        date_end=request.POST.get("dateEnd"),
        title=request.POST.get("title"),
        description=request.POST.get("description"),
        repeat=request.POST.get("repeat"),
        reminder=request.POST.get("reminder"),
    )
    if response is not None:
        return response
    return request_success({"hash": event.hash})
