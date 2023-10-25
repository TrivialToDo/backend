from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

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
    return JsonResponse({
        "code": 200,
        "data": {
            "event": res.serialize()
        }
    })
