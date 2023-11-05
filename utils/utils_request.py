from django.http import JsonResponse


def request_success(data=None):
    if data is None:
        data = {}
    return JsonResponse({
        "code": 200,
        "data": data
    })
