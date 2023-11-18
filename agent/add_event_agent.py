import json
from .base_agent import BaseAgent
from typing import Dict, Any, Tuple
import logging
from .memory_manager import MemoryManager
from user.models import User
from event.models import Event
from asgiref.sync import sync_to_async


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
                "get_current_schedule": self.get_current_schedule,
                "send_message": self.send_message,
                "add_event_to_schedule": self.add_event_to_schedule,
            }
        )
        self.memory_manager = MemoryManager(user.wechat_id)
        self.user = user

    async def add_event_to_schedule(
        self,
        event: str,
        start_time: str,
        whether_need_remind: bool,
        end_time: str = "",
        remind_time_relative_to_start_time: Dict[str, Any] = {},
    ) -> Tuple[str, bool, bool]:
        logging.info(
            f"🔧 {self.__str__()} Function Calling: add_event_to_schedule("
            + f"{event}, {start_time}, {end_time}, {whether_need_remind}, {remind_time_relative_to_start_time})"
        )
        await sync_to_async(Event.create_event)(
            user=self.user,
            time_start={
                "hour": int(start_time[11:13]),
                "minute": int(start_time[14:16]),
            },
            date_start=start_time[:10],
            time_end={
                "hour": int(end_time[11:13]) if end_time else None,
                "minute": int(end_time[14:16]) if end_time else None,
            },
            date_end=end_time[:10] if end_time else None,
            title=event,
            description=event,
            repeat="never",
        )
        return (
            f"Added event {event} to schedule. Start time: {start_time}"
            + (f" End time: {end_time}" if end_time else "")
            + (
                f" Remind time relative to start time: {remind_time_relative_to_start_time}"
                if whether_need_remind
                else "No need to remind."
            ),
            True,
            False,
        )

    def __str__(self) -> str:
        return "AddEventAgent"
