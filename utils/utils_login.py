import jwt
from functools import wraps
from datetime import datetime, timedelta
from backend import settings
from utils.utils_request import request_fail
from user.models import User


def login_check(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            token = request.headers['Authorization'].replace('Bearer ', '')
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user']['id']
            generate_time = payload['generate_time']
            generate_time = datetime.strptime(generate_time, '%Y-%m-%dT%H:%M:%S.%fZ')
            if datetime.now() - generate_time > timedelta(seconds=User.JWT_expire_time):
                request_fail(401, 'token expired')
            user = User.objects.filter(id=user_id).first()
            if user is None:
                return request_fail(405, 'invalid JWT')
            return func(request, *args, **kwargs, user=user)
        except jwt.exceptions.DecodeError:
            return request_fail(405, 'invalid JWT')

    return wrapper
