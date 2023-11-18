import json
from .base_agent import BaseAgent
from typing import Dict, Any, Tuple
import logging
from .memory_manager import MemoryManager
from user.models import User


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

    async def modify_event_to_schedule(
        self,
        event: str,
        start_time: str,
        new_event: str = "",
        new_start_time: str = "",
        new_whether_need_remind: bool | None = None,
        new_end_time: str = "",
        new_remind_time_relative_to_start_time: Dict[str, Any] = {},
    ) -> Tuple[str, bool, bool]:
        logging.info(
            f"🔧 {self.__str__()} Function Calling: modify_event_to_schedule("
            + f"{event}, {start_time}, {new_event}, {new_start_time}, {new_whether_need_remind}, {new_end_time}, {new_remind_time_relative_to_start_time})"
        )
        return (
            "假装修改了日程",
            True,
            False,
        )

    def __str__(self) -> str:
        return "ModifyEventAgent"
