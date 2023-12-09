import json
from .base_agent import BaseAgent
from typing import Dict, Tuple
import logging
from .memory_manager import MemoryManager
from user.models import User
from event.models import Event


class ModifyEventAgent(BaseAgent):
    def __init__(self, user: User) -> None:
        super().__init__()
        with open("agent/prompt/modify_event_agent.txt") as f:
            self.system_prompt = f.read()
        with open("agent/functions/modify_event_agent.json") as f:
            self.functions.extend(json.load(f))
        self.available_function.update(
            {
                "get_current_time": self.get_current_time,
                "get_day_schedule": self.get_day_schedule,
                "send_message": self.send_message,
                "modify_event_to_schedule": self.modify_event_to_schedule,
                "end_conversation": self.end_conversation,
            }
        )
        self.memory_manager = MemoryManager(user.wechat_id)
        self.user = user

    def modify_event_to_schedule(
        self,
        title: str,
        start_time: str,
        new_title: str = "",
        new_description: str = "",
        new_start_time: str = "",
        new_end_time: str = "",
        new_reminder: Dict[str, str] = {},
    ) -> Tuple[str, bool, bool]:
        logging.info(
            f"🔧 {self.__str__()} Function Calling: modify_event_to_schedule({title}, {start_time}, {new_title}, {new_description}, {new_start_time}, {new_end_time}, {new_reminder})"
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
        res = res[0]
        if new_title:
            res.title = new_title
        if new_description:
            res.description = new_description
        if new_start_time:
            res.timeStart = {
                "hour": int(new_start_time[11:13]),
                "minute": int(new_start_time[14:16]),
            }
            res.dateStart = new_start_time[:10]
        if new_end_time:
            res.timeEnd = {
                "hour": int(new_end_time[11:13]),
                "minute": int(new_end_time[14:16]),
            }
            res.dateEnd = new_end_time[:10]
        if new_reminder:
            res.reminder = {
                "hour": int(new_reminder["time"][11:13]),
                "minute": int(new_reminder["time"][14:16]),
            }
        res.save()
        return (
            f"Modify Event {title}\ndescription: {res.description}\nstart time: {res.dateStart} {res.timeStart}\nend time: {res.dateEnd} {res.timeEnd}\nreminder time: {res.reminder}",
            True,
            False,
        )

    def __str__(self) -> str:
        return "ModifyEventAgent"
