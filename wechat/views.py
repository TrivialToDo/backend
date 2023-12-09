import json
from datetime import datetime

from django.views.decorators.http import require_http_methods

from utils.utils_logger import get_logger
from utils.utils_request import request_success
from agent.views import agent_main
from user.models import User
import asyncio

import backoff
import openai
import os
import base64

# Create your views here.

@backoff.on_exception(backoff.expo, Exception, max_time=60)
def process_audio(audio_path: str) -> str:
    message = openai.audio.translations.create(
        file=open(audio_path, 'rb'),
        model='whisper-1',
        prompt='你需要将这段话转换成简体中文:\n',
        response_format='text',
        temperature=0
    )
    return message


@require_http_methods(['POST'])
def recv_msg(req):
    body = json.loads(req.body.decode('utf-8'))
    type = body['type']
    wechat_id = body['id']
    nickname = body['name']
    msg_time = body['date']
    msg_time = datetime.strptime(msg_time, '%Y-%m-%dT%H:%M:%S.%fZ')
    get_logger().info(msg_time)
    user = User.objects.filter(wechat_id=wechat_id).first()
    if user is None:
        user = User.objects.create(wechat_id=wechat_id, nickname=nickname)

    if type == 'text' and body['content'] == '查日程':
        return request_success({
            "type": "text",
            "content": user.generate_temp_token()
        })

    if user.agent_deal:
        return request_success({
            "type": "text",
            "content": "get off!"
        })
    
    if type == 'audio':
        audio_name = wechat_id
        audio_path = f'./{audio_name}.mp3'
        with open(audio_path, 'wb') as f:
            f.write(base64.b64decode(body['content']))
        body['content'] = process_audio(audio_path)
        os.remove(audio_path)

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
