from datetime import datetime, timedelta
from agent.base_agent import BaseAgent
from schedule.views import get_day_event
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
        self.available_function = {
            "send_message": self.send_message,
            "send_schedule": self.send_schedule,
            "get_web_url": self.get_web_url,
        }

    def send_message(self, message: str) -> Tuple[str, bool, bool]:
        logging.info(f"🔧 {self.__str__()} Function Calling: send_message({message})")
        return message, True, True
    
    def send_schedule(self, date: str) -> Tuple[str, bool, bool]:
        logging.info(f"🔧 {self.__str__()} Function Calling: send_schedule({date})")
        events = []
        for i in range(7):
            _date = datetime.strptime(date, "%Y-%m-%d").date()
            _date += timedelta(days=i)
            r = get_day_event(_date, self.user)
            events.extend([e for e in r])
        #TODO
        return date, True, False
    
    def get_web_url(self) -> Tuple[str, bool, bool]:
        logging.info(f"🔧 {self.__str__()} Function Calling: get_web_url()")
        token = self.user.generate_temp_token()
        return f"todo.yuan.cf/login?token={token}", True, False

    def __str__(self) -> str:
        return "ChatAgent"
