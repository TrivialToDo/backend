from agent.base_agent import BaseAgent
from user.models import User
from typing import Tuple
import logging
import json


class ChatAgent(BaseAgent):
    def __init__(self, user: User) -> None:
        super().__init__()
        self.user = user
        with open("agent/prompt/chat_agent.txt", encoding="utf-8") as f:
            self.system_prompt = f.read()
        with open("agent/functions/chat_agent.json", encoding="utf-8") as f:
            self.functions = json.load(f)
        self.available_function = {"send_message": self.send_message}

    def send_message(self, message: str) -> Tuple[str, bool, bool]:
        logging.info(f"🔧 {self.__str__()} Function Calling: send_message({message})")
        return message, True, True

    def __str__(self) -> str:
        return "ChatAgent"
