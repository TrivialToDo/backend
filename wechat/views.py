import json
from datetime import datetime

from django.views.decorators.http import require_http_methods

from utils.utils_logger import get_logger
from utils.utils_request import request_success
from agent.views import agent_main
from user.models import User
from wechat.utils import send_message
import backoff
import openai
import os
import base64

from config import config

import backoff
from typing import List, Dict, Tuple

from agent.add_event_agent import AddEventAgent

# Create your views here.
group_msg_buffer: Dict[str, List[Tuple[str, str]]] = {}


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


@backoff.on_exception(backoff.expo, Exception, max_time=60)
def process_image(base64_image) -> str:
    response = openai.chat.completions.create(
        model='gpt-4-vision-preview',
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract all text from the image. You should only respond with the text in the image.\nIf the image is about a conversation, you should use User1, User2... to represent different users. You can use avatar to identify different users. Different user has different avatar while the same user has the same avatar."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=4096,
        temperature=0
    )
    return response.choices[0].message.content


@backoff.on_exception(backoff.constant, Exception, interval=3, max_time=60)
def chat_completion(
        messages: List[Dict[str, str]], functions: List = [], max_tokens=2048, type="text"
) -> Dict[str, str]:
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=functions,
        tool_choice="auto",
        max_tokens=max_tokens,
        temperature=0.05,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        # response_format={
        #     "type": type
        # },
    )
    return response.choices[0].message


@require_http_methods(['POST'])
def recv_msg(req):
    body = json.loads(req.body.decode('utf-8'))
    _type = body['type']
    wechat_id = body['id']

    nickname = body['name']
    msg_time = body['date']
    msg_time = datetime.strptime(msg_time, '%Y-%m-%dT%H:%M:%S.%fZ')
    get_logger().info(msg_time)

    is_room = body['isRoom']
    if is_room:
        if _type == 'audio':
            audio_name = wechat_id
            audio_path = f'./{audio_name}.mp3'
            with open(audio_path, 'wb') as f:
                f.write(base64.b64decode(body['content']))
            body['content'] = process_audio(audio_path)
            os.remove(audio_path)

        if _type == 'image':
            body['content'] = process_image(body['content'])

        recv_room_msg(body)

        return request_success({
            "type": "noreply",
            "content": ""
        })

    user = User.objects.filter(wechat_id=wechat_id).first()
    if user is None:
        user = User.objects.create(wechat_id=wechat_id, nickname=nickname)

    if _type == 'text' and body['content'] == '查日程':
        return request_success({
            "type": "text",
            "content": f"{config.FRONTEND_URL}/login?token={user.generate_temp_token()}"
        })

    if user.agent_deal:
        return request_success({
            "type": "text",
            "content": "get off!"
        })

    if _type == 'audio':
        audio_name = wechat_id
        audio_path = f'./{audio_name}.mp3'
        with open(audio_path, 'wb') as f:
            f.write(base64.b64decode(body['content']))
        body['content'] = process_audio(audio_path)
        os.remove(audio_path)

    if _type == 'image':
        body['content'] = process_image(body['content'])

    try:
        user.agent_deal = True
        user.save()

        message = agent_main(body['content'], user)
    except Exception as e:
        get_logger().error(e)

    user.agent_deal = False
    user.save()

    if type(message) == str:
        return request_success({
            "type": "text",
            "content": message
        })
    elif type(message) == tuple:
        return request_success({
            "type": "image",
            "content": message[0]
        })


def recv_room_msg(body):
    global group_msg_buffer
    roomid = body['roomid']
    if roomid in group_msg_buffer.keys():
        group_msg_buffer[roomid].append((body['id'], body['content']))
    else:
        group_msg_buffer[roomid] = []
        group_msg_buffer[roomid].append((body['id'], body['content']))


def process_room_msgs():
    global group_msg_buffer
    print("processing room msg")
    print(len(group_msg_buffer.keys()))
    for key in group_msg_buffer.keys():
        msgs = group_msg_buffer[key]
        process_room_msg(msgs)
    group_msg_buffer = {}


def process_room_msg(messages: List[Tuple[str, str]]):
    print("processing room msg")
    print(messages)
    user_input = ["\"" + message[0] + "\": " + message[1] for message in messages]
    user_input = "\n".join(user_input)
    with open("prompt.txt", "r", encoding="utf-8") as f:
        prompt = f.read()
    request_messages = [
        {
            "role": "system",
            "content": prompt,
        },
        {
            "role": "user",
            "content": user_input,
        }
    ]
    response = chat_completion(request_messages, type="json_object")
    response = json.loads(response, encoding="utf-8")
    if not response["needProcess"]:
        return
    process = response["process"]
    for todo in process:
        user_id = todo["userId"]
        user_input = todo["userInput"]
        # 调用 add_event_agent
        # user
        user = User.objects.filter(wechat_id=user_id)
        if len(user) == 0:
            continue
        user = user[0]
        planning_agent = AddEventAgent(user)
        message = planning_agent(user_input)
        # send
        send_message(user, 'text', message)
