import json
from .base_agent import BaseAgent
from .add_event_agent import AddEventAgent
from .delete_event_agent import DeleteEventAgent
from .modify_event_agent import ModifyEventAgent
from .chat_agent import ChatAgent
from typing import Tuple
import logging
from user.models import User
from .models import Conversation
import pickle


class ScheduleAgent(BaseAgent):
    def __init__(self, user: User) -> None:
        super().__init__()
        with open("agent/prompt/schedule_agent.txt", "r", encoding="utf-8") as f:
            self.system_prompt = f.read()
        with open("agent/functions/schedule_agent.json", "r", encoding="utf-8") as f:
            self.functions = json.load(f)
        self.available_function = {
            "call_add_event_agent": self.call_add_event_agent,
            "call_delete_event_agent": self.call_delete_event_agent,
            "call_modify_event_agent": self.call_modify_event_agent,
            "call_chat_agent": self.call_chat_agent,
            "recall_previous_conversation": self.recall_previous_conversation,
        }
        self.user = user

    def call_add_event_agent(self, user_input: str) -> Tuple[str, bool, bool]:
        logging.info(
            f"🔧 {self.__str__()} Function Calling: call_add_event_agent({user_input})"
        )
        planning_agent = AddEventAgent(self.user)
        return planning_agent(user_input), True, False

    def call_delete_event_agent(self, user_input: str) -> Tuple[str, bool, bool]:
        logging.info(
            f"🔧 {self.__str__()} Function Calling: call_delete_event_agent({user_input})"
        )
        delete_event_agent = DeleteEventAgent(self.user)
        return delete_event_agent(user_input), True, False

    def call_modify_event_agent(self, user_input: str) -> Tuple[str, bool, bool]:
        logging.info(
            f"🔧 {self.__str__()} Function Calling: call_modify_event_agent({user_input})"
        )
        modify_event_agent = ModifyEventAgent(self.user)
        return modify_event_agent(user_input), True, False

    def call_chat_agent(self, user_input: str) -> Tuple[str, bool, bool]:
        logging.info(
            f"🔧 {self.__str__()} Function Calling: call_chat_agent({user_input})"
        )
        return (
            "Hello World! Welcome to contact with us by email: lkm20@mails.tsinghua.edu.cn",
            True,
            False,
        )

    def recall_previous_conversation(self, user_input: str) -> Tuple[str, bool, bool]:
        logging.info(
            f"🔧 {self.__str__()} Function Calling: recall_previous_conversation({user_input})"
        )
        conversation = Conversation.objects.filter(wechat_id=self.user.wechat_id).first()
        if not conversation:
            return "No previous conversation. You should call new agent.", False, False
        if conversation.type == "AddEventAgent":
            planning_agent = AddEventAgent(self.user)
            return (
                planning_agent(
                    user_input, pickle.loads(conversation.messages)
                ),
                True,
                False,
            )
        elif conversation.type == "DeleteEventAgent":
            delete_event_agent = DeleteEventAgent(self.user)
            return (
                delete_event_agent(
                    user_input, pickle.loads(conversation.messages)
                ),
                True,
                False,
            )
        elif conversation.type == "ModifyEventAgent":
            modify_event_agent = ModifyEventAgent(self.user)
            return (
                modify_event_agent(
                    user_input, pickle.loads(conversation.messages)
                ),
                True,
                False,
            )
        elif conversation.type == "ChatAgent":
            chat_agent = ChatAgent(self.user)
            return (
                chat_agent(
                    user_input, pickle.loads(conversation.messages)
                ),
                True,
                False,
            )
        else:
            logging.info(f"😱 {self.__str__()} Unknown conversation type: {conversation.type}")
            return f"Unknown conversation type: {conversation.type}", False, False

    def __call__(self, user_input: str) -> str:
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
            response = self.chat_completion(messages, self.functions)
            message, end, _ = self.handle_ai_response(response)
            messages.append(response)
            messages.extend(message)
            if end:
                return message[-1]["content"]

    def __str__(self) -> str:
        return "ScheduleAgent"
