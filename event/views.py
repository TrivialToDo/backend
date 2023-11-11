from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from utils.utils_login import login_check
from utils.utils_request import request_success, request_fail
from .models import Event
from user.models import User


# Create your views here.

@login_check
@require_http_methods(['GET', 'DELETE'])
def deal_event(request, hash: str, user: User = None):
    if request.method == 'GET':
        return get_event(request, hash, user)
    elif request.method == 'DELETE':
        return del_event(request, hash, user)


def get_event(request, hash: str, user: User = None):
    res = Event.objects.filter(hash=hash, user=user).first()
    if res is None:
        return request_fail(404, "event not found")
    return request_success({
        "event": res.serialize()
    })


def del_event(request, hash: str, user: User = None):
    res = Event.objects.filter(hash=hash, user=user).first()
    if res is None:
        return request_fail(404, "event not found")
    res.delete()
    return request_success({
        "msg": "Succeed"
    })
