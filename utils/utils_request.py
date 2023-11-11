from django.http import JsonResponse


def request_success(data=None):
    if data is None:
        data = {}
    return JsonResponse({
        "code": 200,
        "data": data
    })


def request_fail(code: int, msg: str):
    return JsonResponse({
        "code": code,
        "data": {
            "msg": msg
        }
    }, status=code)
