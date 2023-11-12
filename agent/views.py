from django.shortcuts import render
from wechat.utils import send_message
from user.models import User
from .schedule_agent import ScheduleAgent


# Create your views here.

async def agent_main(user_input: str, user: User) -> None:
    # send_message(
    #     user,
    #     _type="text",
    #     content="hello world"
    # )
    # pass
    schedule_agent = ScheduleAgent(user.wechat_id)
    await schedule_agent(user_input)
