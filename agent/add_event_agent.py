import json
from .base_agent import BaseAgent
from typing import Dict, Tuple
import logging
from .memory_manager import MemoryManager
from user.models import User
from event.models import Event


class AddEventAgent(BaseAgent):
    def __init__(self, user: User) -> None:
        super().__init__()
        with open("agent/prompt/add_event_agent.txt") as f:
            self.system_prompt = f.read()
        with open("agent/functions/add_event_agent.json") as f:
            self.functions.extend(json.load(f))
        self.available_function.update(
            {
                "get_current_time": self.get_current_time,
                "get_day_schedule": self.get_day_schedule,
                "send_message": self.send_message,
                "add_event_to_schedule": self.add_event_to_schedule,
                "end_conversation": self.end_conversation,
            }
        )
        self.memory_manager = MemoryManager(user.wechat_id)
        self.user = user

    def add_event_to_schedule(
        self,
        title: str,
        description: str,
        start_time: str,
        end_time: str = "",
        reminder: Dict[str, str] = {},
    ) -> Tuple[str, bool, bool]:
        logging.info(
            f"🔧 {self.__str__()} Function Calling: add_event_to_schedule("
            + f"title={title}, description={description}, start_time={start_time}, end_time={end_time}, reminder={reminder})"
        )

        e, response = Event.create_event(
            user=self.user,
            time_start={
                "hour": int(start_time[11:13]),
                "minute": int(start_time[14:16]),
            },
            date_start=start_time[:10],
            time_end={
                "hour": int(end_time[11:13]),
                "minute": int(end_time[14:16]),
            }
            if end_time
            else None,
            date_end=end_time[:10] if end_time else None,
            title=title,
            description=description,
            repeat="never",
            reminder={
                "hour": int(reminder["time"][11:13]),
                "minute": int(reminder["time"][14:16]),
            }
            if reminder
            else None,
        )
        if response:
            return (
                response.json["data"]["msg"],
                True,
                False,
            )
        else:
            return (
                "成功添加日程: "
                + title
                + "\n"
                + "description: "
                + description
                + "\n"
                + "start_time: "
                + start_time
                + "\n"
                + "end_time: "
                + end_time
                + "\n"
                + "reminder time: "
                + reminder["time"]
                + "\n"
                + "reminder type: "
                + reminder["type"],
                True,
                False,
            )

    def __str__(self) -> str:
        return "AddEventAgent"
