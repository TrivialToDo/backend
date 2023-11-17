import json
from datetime import datetime

from django.views.decorators.http import require_http_methods
from utils.utils_request import request_success
from agent.views import agent_main
from user.models import User


# Create your views here.


@require_http_methods(['POST'])
def recv_msg(req):
    return request_success({
        "type": "text",
        "content": "fuck you!"
    })
    body = json.loads(req.body.decode('utf-8'))
    wechat_id = body['id']
    nickname = body['name']
    msg_time = body['data']
    msg_time = datetime.strptime(msg_time, '%Y-%m-%dT%H:%M:%S.%fZ')
    print(msg_time)
    user = User.objects.filter(wechat_id=wechat_id).first()
    if user is None:
        user = User.objects.create(wechat_id=wechat_id, nickname=nickname)
    if user.agent_deal == True:
        return request_success({
            "type": "text",
            "content": "get off!"
        })
    user.agent_deal = True
    user.save()

    agent_main(body['content'], user)

    user.agent_deal = False
    user.save()

    return request_success({
        "type": "no_reply"
    })
