from django.shortcuts import render
from wechat.utils import send_message
from user.models import User
from event.models import Event


# Create your views here.

async def agent_main(user_input: str, user: User) -> None:
    send_message(
        user,
        _type="text",
        content="hello world"
    )
    Event.create_event(
        user=user,
        time_start={
            'hour': 0,
            'minute': 0
        },
        date_start='2021-01-01',
        time_end={
            'hour': 0,
            'minute': 0
        },
        date_end='2021-01-01',
        title='test',
        description='test',
        repeat='never'
    )
    pass
