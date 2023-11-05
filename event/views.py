from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from utils.utils_request import request_success
from .models import Event


# Create your views here.


@require_http_methods(['GET'])
def get_event(request, hash: str):
    res = Event.objects.filter(hash=hash).first()
    if res is None:
        return JsonResponse({
            "code": 404,
            "data": {
                "msg": "event not found"
            }
        }, status=404)
    return request_success({
        "event": res.serialize()
    })
