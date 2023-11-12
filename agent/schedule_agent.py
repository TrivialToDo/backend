import json
from base_agent import BaseAgent
from add_event_agent import AddEventAgent
from typing import Tuple
import logging
from user.models import User
from models import Conversation


class ScheduleAgent(BaseAgent):
    def __init__(self, user: User) -> None:
        super().__init__()
        with open("agent/prompt/schedule_agent.txt", "r", encoding="utf-8") as f:
            self.system_prompt = f.read()
        with open("agent/functions/schedule_agent.json", "r", encoding="utf-8") as f:
            self.functions = json.load(f)
        self.available_function = {
            "call_add_event_agent": self.call_add_event_agent,
            "call_remove_event_agent": self.call_remove_event_agent,
            "call_modify_event_agent": self.call_modify_event_agent,
            "call_chat_agent": self.call_chat_agent,
            "recall_previous_conversation": self.recall_previous_conversation,
        }
        self.user = user

    async def call_add_event_agent(self, user_input: str) -> Tuple[str, bool, bool]:
        logging.info(
            f"🔧 {self.__str__()} Function Calling: call_add_event_agent({user_input})"
        )
        planning_agent = AddEventAgent(self.user)
        return await planning_agent(user_input), True, False

    async def call_remove_event_agent(self, user_input: str) -> Tuple[str, bool, bool]:
        logging.info(
            f"🔧 {self.__str__()} Function Calling: call_remove_event_agent({user_input})"
        )
        return (
            "Hello World! Welcome to contact with us by email: lkm20@mails.tsinghua.edu.cn",
            True,
            False,
        )

    async def call_modify_event_agent(self, user_input: str) -> Tuple[str, bool, bool]:
        logging.info(
            f"🔧 {self.__str__()} Function Calling: call_modify_event_agent({user_input})"
        )
        return (
            "Hello World! Welcome to contact with us by email: lkm20@mails.tsinghua.edu.cn",
            True,
            False,
        )

    async def call_chat_agent(self, user_input: str) -> Tuple[str, bool, bool]:
        logging.info(
            f"🔧 {self.__str__()} Function Calling: call_chat_agent({user_input})"
        )
        return (
            "Hello World! Welcome to contact with us by email: lkm20@mails.tsinghua.edu.cn",
            True,
            False,
        )

    async def recall_previous_conversation(self, user_input: str) -> Tuple[str, bool, bool]:
        conversation = Conversation.objects.filter(wechat_id=self.user.wechat_id).first()
        if not conversation:
            return "No previous conversation", False, False
        if conversation.type == "add_event":
            planning_agent = AddEventAgent(self.user)
            return await planning_agent(user_input, json.loads(conversation.messages)), True, False
        else:
            logging.error(f"😱 {self.__str__()} Unknown conversation type: {conversation.type}")
            return "Hello World! Welcome to contact with us by email: lkm20@mails.tsinghua.edu.cn", True, False

    async def __call__(self, user_input: str) -> str:
        logging.info(f"😄 {self.__str__()} Called.")
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
        while True:
            response = await self.chat_completion(messages, self.functions)
            message, end, need_save = await self.handle_ai_response(response)
            messages.append(response)
            messages.extend(message)
            if end:
                return message[0]["content"]

    def __str__(self) -> str:
        return "ScheduleAgent"
