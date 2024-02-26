from django.shortcuts import render
import json
from django.views.decorators.http import require_http_methods
from utils.utils_request import request_success, request_fail
from user.models import User


# Create your views here.


@require_http_methods(['POST'])
def login(request):
    body = json.loads(request.body.decode('utf-8'))
    token = body['token']
    user = User.objects.filter(temp_token=token).first()
    if user is None:
        return request_fail(405, "Invalid token")
    return request_success({
        "jwt": user.generate_JWT()
    })
