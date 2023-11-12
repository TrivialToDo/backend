import json
from datetime import datetime

from django.views.decorators.http import require_http_methods
from utils.utils_request import request_success
from agent.views import agent_main
from user.models import User
import asyncio


# Create your views here.


@require_http_methods(['POST'])
def recv_msg(req):
    body = json.loads(req.body.decode('utf-8'))
    wechat_id = body['id']
    nickname = body['name']
    msg_time = body['data']
    msg_time = datetime.strptime(msg_time, '%Y-%m-%dT%H:%M:%S.%fZ')
    print(msg_time)
    user = User.objects.filter(wechat_id=wechat_id).first()
    if user is None:
        user = User.objects.create(wechat_id=wechat_id, nickname=nickname)

    message = asyncio.run(agent_main(body['content'], user))

    return request_success({
        "type" : "text",
        "content" : message
    })
