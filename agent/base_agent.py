from typing import List, Dict, Tuple
import json
import abc
import os
import logging
import openai
from datetime import datetime
import pickle

from schedule.views import get_day_event
from .models import Conversation

import backoff


class BaseAgent:
    def __init__(self) -> None:
        if not "OPENAI_API_KEY" in os.environ:
            logging.error("❌ 🤖 OPENAI_API_KEY environment variable not set")
            raise Exception("OPENAI_API_KEY environment variable not set")
        with open("agent/functions/memory_manager.json", "r", encoding="utf-8") as f:
            self.functions = json.load(f)
        self.available_function = {
            "retrieve_user_behavioral_tendency": self.retrieve_user_behavioral_tendency,
            "add_record_to_memory": self.add_record_to_memory,
            "remove_record_in_memory": self.remove_record_in_memory,
            "update_record_in_memory": self.update_record_in_memory,
        }
        self.ai_response_history = []

    @backoff.on_exception(backoff.constant, Exception, interval=3, max_time=60)
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        functions: List = [],
        max_tokens=1024,
        type="text",
        model="gpt-4",
    ) -> Dict[str, str]:
        logging.info(f"🤖 {self.__str__()} Function Calling: chat_completion()")
        if model == "gpt-4-1106-preview":
            response = openai.chat.completions.create(
                model=model,
                messages=messages,
                tools=functions,
                tool_choice="auto",
                max_tokens=max_tokens,
                temperature=0.05,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                response_format={"type": type},
            )
        else:
            response = openai.chat.completions.create(
                model=model,
                messages=messages,
                tools=functions,
                tool_choice="auto",
                max_tokens=max_tokens,
                temperature=0.05,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
            )
        logging.info(f"🤖 {self.__str__()} Function Called.")
        return response.choices[0].message

    def handle_ai_response(self, response) -> Tuple[List[Dict[str, str]], bool, bool]:
        content = response.content
        if content:
            logging.info(f"💬 {self.__str__()}: " + content.replace("\n", ""))

        messages = []
        tool_calls = response.tool_calls
        end, need_save = False, False
        if tool_calls:
            for tool_call in tool_calls:
                tool_id = tool_call.id
                message = {}
                function_name = tool_call.function.name
                message["role"] = "tool"
                message["tool_call_id"] = tool_id
                try:
                    function_to_call = self.available_function[function_name]
                except KeyError as _:
                    message["content"] = f"No function named {function_name}."
                    logging.info(
                        f"🙅{self.__str__()}: No function named {function_name}."
                    )
                    messages.append(message)
                try:
                    function_args = json.loads(tool_call.function.arguments)
                except Exception as _:
                    message[
                        "content"
                    ] = f"Error parsing JSON for function '{function_name}' arguments: {tool_call.function.arguments}"
                    logging.info(
                        f"🙅 {self.__str__()}: Error parsing JSON for function '{function_name}' arguments: {tool_call.function.arguments}."
                    )
                    messages.append(message)
                try:
                    content, _end, _need_save = function_to_call(**function_args)
                    message["content"] = content
                    if _end:
                        end = True
                    if _need_save:
                        need_save = True
                    messages.append(message)
                except Exception as e:
                    message[
                        "content"
                    ] = f"Error calling function {function_name} with args {function_args}: {str(e)}."
                    logging.error(
                        f"🙅 {self.__str__()}: Error calling function {function_name} with args {function_args}: {str(e)}."
                    )
                    messages.append(message)

        self.ai_response_history.append(
            {
                "content": content,
                "first_tool": tool_calls[0].function.name if tool_calls else None,
            }
        )
        if len(self.ai_response_history) > 10:
            return "我不知道该说什么，但是花太多钱了，你可以再试一次。", True, False
        if (
            len(self.ai_response_history) > 1
            and self.ai_response_history[-1] == self.ai_response_history[-2]
        ):
            return "我不知道该说什么，但是 OpenAI 好像崩了，你可以再试一次。", True, False

        return messages, end, need_save

    def get_current_time(self) -> Tuple[str, bool, bool]:
        logging.info(f"🔧 {self.__str__()} Function Calling: get_current_time()")
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S"), False, False

    def _process_get_day_schedule(self, r) -> str:
        return "\n".join([i.serialize() for i in r])

    def get_day_schedule(self, date: str) -> Tuple[str, bool, bool]:
        logging.info(f"🔧 {self.__str__()} Function Calling: get_day_schedule({date})")

        _date = datetime.strptime(date, "%Y-%m-%d").date()
        r = get_day_event(_date, self.user)
        return self._process_get_day_schedule(r), False, False

    def send_message(self, question: str) -> Tuple[str, bool, bool]:
        logging.info(f"🔧 {self.__str__()} Function Calling: send_message({question})")
        return question, True, True

    def end_conversation(self, reason: str) -> Tuple[str, bool, bool]:
        logging.info(f"🔧 {self.__str__()} Function Calling: end_conversation({reason})")
        return f"Conversation ended: {reason}", True, False

    def retrieve_user_behavioral_tendency(self, query: str) -> Tuple[str, bool, bool]:
        logging.info(
            f"🔧 {self.__str__()} Function Calling: retrieve_user_behavioral_tendency({query})"
        )
        results = self.memory_manager.search(query)
        content = f"Search results for {query}:\n" + "\n".join(results)
        return content, False, False

    def add_record_to_memory(self, text: str) -> Tuple[str, bool, bool]:
        logging.info(
            f"🔧 {self.__str__()} Function Calling: add_record_to_memory({text})"
        )
        self.memory_manager.add(text)
        return f"Add {text} to memory.", False, False

    def remove_record_in_memory(self, text: str) -> Tuple[str, bool, bool]:
        logging.info(
            f"🔧 {self.__str__()} Function Calling: remove_record_in_memory({text})"
        )
        self.memory_manager.delete(text)
        return f"Remove {text} from memory.", False, False

    def update_record_in_memory(
        self, text: str, new_text: str
    ) -> Tuple[str, bool, bool]:
        logging.info(
            f"🔧 {self.__str__()} Function Calling: update_record_in_memory({text}, {new_text})"
        )
        self.memory_manager.update(text, new_text)
        return f"Update {text} to {new_text}.", False, False

    def __call__(self, user_input: str, past_messages: List[Dict] | None = None) -> str:
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
            response = self.chat_completion(messages, self.functions)
            message, end, need_save = self.handle_ai_response(response)
            messages.append(response)
            messages.extend(message)
            if end:
                if need_save:
                    Conversation.delete(self.user.wechat_id)
                    logging.info(f"📝 {self.__str__()} Saving conversation...")
                    binary_messages = pickle.dumps(messages)
                    Conversation.add(self.user.wechat_id, binary_messages, self.__str__())
                    logging.info(f"✅ 📝 {self.__str__()} Saved conversation.")
                else:
                    Conversation.delete(self.user.wechat_id)
                return message[-1]["content"]

    @abc.abstractmethod
    def __str__(self) -> str:
        pass
