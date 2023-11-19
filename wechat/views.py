import json
from datetime import datetime

from django.views.decorators.http import require_http_methods

from utils.utils_logger import get_logger
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
    msg_time = body['date']
    msg_time = datetime.strptime(msg_time, '%Y-%m-%dT%H:%M:%S.%fZ')
    get_logger().info(msg_time)
    user = User.objects.filter(wechat_id=wechat_id).first()
    if user is None:
        user = User.objects.create(wechat_id=wechat_id, nickname=nickname)

    if body['content'] == '查日程':
        return request_success({
            "type": "text",
            "content": user.generate_temp_token()
        })

    if user.agent_deal:
        return request_success({
            "type": "text",
            "content": "get off!"
        })

    try:
        user.agent_deal = True
        user.save()

        message = asyncio.run(agent_main(body['content'], user))
    except Exception as e:
        get_logger().error(e)

    user.agent_deal = False
    user.save()

    return request_success({
        "type": "text",
        "content": message
    })
