import json
from .base_agent import BaseAgent
from typing import Dict, Tuple, List
import logging
from .memory_manager import MemoryManager
from user.models import User
from event.models import Event
from datetime import datetime, timedelta
from schedule.views import get_day_event
from django.db.models.manager import BaseManager
import backoff


class OptimizeAgent(BaseAgent):
    def __init__(self, user: User) -> None:
        super().__init__()
        with open("agent/prompt/optimize_agent.txt", "r", encoding="utf-8") as f:
            self.system_prompt = f.read()
        with open("agent/functions/optimize_agent.json", "r", encoding="utf-8") as f:
            self.functions = json.load(f)
        self.available_function = {
            "get_current_time": self.get_current_time,
            "send_message": self.send_message,
            "optimize_day_schedule": self.optimize_day_schedule,
            "optimize_week_schedule": self.optimize_week_schedule,
            "end_conversation": self.end_conversation,
        }
        self.user = user
        with open("prompt/optimize_events.txt", "r", encoding="utf-8") as f:
            self.optimize_events_prompt = f.read()

    @backoff.on_exception(backoff.constant, Exception, interval=3, max_tries=3)
    def optimize_events(self, events: List[Event]) -> int:
        messages = [
            {
                "role": "system",
                "content": self.optimize_events_prompt,
            },
            {
                "role": "user",
                "content": json.dumps([i.serialize() for i in events], ensure_ascii=False),
            },
        ]
        response = self.chat_completion(messages, max_tokens=2048, type="json_object")
        new_events = json.loads(response, encoding="utf-8")
        num = 0
        Event.remove_all_events(user=self.user)
        for i in new_events:
            Event.create_event(
                user=self.user,
                time_start=i.get("timeStart", None),
                date_start=i.get("dateStart", None),
                time_end=i.get("timeEnd", None),
                date_end=i.get("dateEnd", None),
                title=i.get("title", None),
                description=i.get("description", None),
                repeat=i.get("repeat", None),
                reminder=i.get("reminder", None),
            )
            num += 1
        return num

    def optimize_day_schedule(self, date: str) -> Tuple[str, bool, bool]:
        logging.info(
            f"🔧 {self.__str__()} Function Calling: optimize_day_schedule("
            + f"date={date})"
        )
        _date = datetime.strptime(date, "%Y-%m-%d").date()
        r = get_day_event(_date, self.user)
        events = [e for e in r]
        try:
            num = self.optimize_events(events)
            return f"Optimize {num} events in total.", True, False
        except Exception as e:
            logging.error(e)
            return e, False, False

    def optimize_week_schedule(self, date: str) -> Tuple[str, bool, bool]:
        logging.info(
            f"🔧 {self.__str__()} Function Calling: optimize_week_schedule("
            + f"date={date})"
        )
        events = []
        for i in range(7):
            _date = datetime.strptime(date, "%Y-%m-%d").date()
            _date += timedelta(days=i)
            r = get_day_event(_date, self.user)
            events.extend([e for e in r])
        try:
            num = self.optimize_events(events)
            return f"Optimize {num} events in total.", True, False
        except Exception as e:
            logging.error(e)
            return e, False, False

    def __str__(self) -> str:
        return "OptimizeAgent"
