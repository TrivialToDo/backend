import json
from .base_agent import BaseAgent
from typing import Dict, Any, List, Tuple
import logging
import csv
from .models import Conversation
from datetime import datetime
from .memory_manager import MemoryManager
from user.models import User
from event.models import Event
from asgiref.sync import sync_to_async
import pickle


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

    async def get_current_time(self) -> Tuple[str, bool, bool]:
        logging.info(f"🔧 {self.__str__()} Function Calling: get_current_time()")
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S"), False, False

    async def get_current_schedule(self) -> Tuple[str, bool, bool]:
        logging.info(f"🔧 {self.__str__()} Function Calling: get_current_schedule()")
        with open("docs/example_schedule.csv", "r", encoding="utf-8") as f:
            reader = csv.reader(f)
        return "\n".join([",".join(row) for row in reader]), False, False

    async def send_message(self, question: str) -> Tuple[str, bool, bool]:
        logging.info(f"🔧 {self.__str__()} Function Calling: send_message({question})")
        return question, True, True

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

    async def __call__(
        self, user_input: str, past_messages: List[Dict] | None = None
    ) -> str:
        logging.info(f"🤓 {self.__str__()} Called.")
        if not past_messages:
            messages = [
                {
                    "role": "system",
                    "content": self.system_prompt,
                },
                {
                    "role": "user",
                    "content": user_input,
                },
            ]
        else:
            messages = past_messages
            messages[-1]["content"] = user_input
        while True:
            response = await self.chat_completion(messages, self.functions)
            message, end, need_save = await self.handle_ai_response(response)
            messages.append(response)
            messages.extend(message)
            if end:
                past_conversation = await sync_to_async(Conversation.objects.filter)(
                    wechat_id=self.user.wechat_id
                )
                if await sync_to_async(past_conversation.exists)():
                    await sync_to_async(past_conversation.delete)()
                if need_save:
                    logging.info(f"📝 {self.__str__()} Saving conversation...")
                    binary_messages = await sync_to_async(pickle.dumps)(messages)
                    new_conversation = await sync_to_async(Conversation.objects.create)(
                        wechat_id=self.user.wechat_id,
                        messages=binary_messages,
                        type="add_event",
                    )
                    await sync_to_async(new_conversation.save)()
                    logging.info(f"✅ 📝 {self.__str__()} Saved conversation.")
                return message[-1]["content"]

    def __str__(self) -> str:
        return "AddEventAgent"
