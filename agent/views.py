from user.models import User
from .schedule_agent import ScheduleAgent


# Create your views here.
def agent_main(user_input: str, user: User) -> str:
    # send_message(
    #     user,
    #     _type="text",
    #     content="hello world"
    # )
    # pass
    schedule_agent = ScheduleAgent(user)
    return schedule_agent(user_input)
