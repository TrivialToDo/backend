import json
from .base_agent import BaseAgent
from typing import Tuple
import logging
from .memory_manager import MemoryManager
from user.models import User
from event.models import Event


class DeleteEventAgent(BaseAgent):
    def __init__(self, user: User) -> None:
        super().__init__()
        with open("agent/prompt/delete_event_agent.txt") as f:
            self.system_prompt = f.read()
        with open("agent/functions/delete_event_agent.json") as f:
            self.functions.extend(json.load(f))
        self.available_function.update(
            {
                "get_current_time": self.get_current_time,
                "get_day_schedule": self.get_day_schedule,
                "send_message": self.send_message,
                "delete_event_to_schedule": self.delete_event_to_schedule,
                "end_conversation": self.end_conversation,
            }
        )
        self.memory_manager = MemoryManager(user.wechat_id)
        self.user = user

    def delete_event_to_schedule(
        self, title: str, start_time: str
    ) -> Tuple[str, bool, bool]:
        logging.info(
            f"🔧 {self.__str__()} Function Calling: delete_event_to_schedule("
            + f"{title}, {start_time})"
        )
        time_start = {
            "hour": int(start_time[11:13]),
            "minute": int(start_time[14:16]),
        }
        res = Event.objects.filter(user=self.user, timeStart=time_start)
        if len(res) > 1:
            res = res.filter(title=title)
        if len(res) == 0:
            return "No such event", False, False
        title = res[0].title
        description = res[0].description
        start_time = res[0].dateStart.isoformat() + " " + res[0].timeStart.isoformat()
        res.delete()
        return (
            f"Delete Event {title}\ndescription: {description}\nstart time: {start_time}",
            True,
            False,
        )

    def __str__(self) -> str:
        return "DeleteEventAgent"
