from typing import Any, List, Dict, Tuple
import json
import abc
import os
import logging
import openai


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

    async def chat_completion(
        self, messages: List[Dict[str, str]], functions: List = []
    ) -> Dict[str, str]:
        try:
            response = openai.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=messages,
                tools=functions,
                tool_choice="auto",
                max_tokens=1024,
                temperature=0.05,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
            )
            return response.choices[0].message
        except Exception as e:
            logging.error(f"❌ 🤖 Chat completion error: {e}")
            return ""

    async def handle_ai_response(
        self, response: Dict[str, str]
    ) -> Tuple[List[Dict[str, str]], bool, bool]:
        if response.get("content"):
            logging.info(f"💬 {self.__str__()}: " + response["content"].replace("\n", ""))

        messages = []
        tool_calls = response.tool_calls
        ask_content = ""
        end, need_save = False, False
        if tool_calls:
            for tool_call in tool_calls:
                message = {}
                function_name = tool_call.function.name
                message["role"] = "function"
                message["name"] = function_name
                try:
                    function_to_call = self.available_function[function_name]
                except KeyError as _:
                    message["content"] = f"No function named {function_name}."
                    logging.info(f"🙅{self.__str__()}: No function named {function_name}.")
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
                    content, _end, _need_save = await function_to_call(**function_args)
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
        return messages, end, need_save

    async def retrieve_user_behavioral_tendency(self, query: str) -> Tuple[str, bool, bool]:
        logging.info(
            f"🔧 {self.__str__()} Function Calling: retrieve_user_behavioral_tendency({query})"
        )
        results = await self.memory_manager.search(query)
        content = f"Search results for {query}:\n" + "\n".join(results)
        return content, False, False

    async def add_record_to_memory(self, text: str) -> Tuple[str, bool, bool]:
        logging.info(
            f"🔧 {self.__str__()} Function Calling: add_record_to_memory({text})"
        )
        await self.memory_manager.add(text)
        return f"Add {text} to memory.", False, False

    async def remove_record_in_memory(self, text: str) -> Tuple[str, bool, bool]:
        logging.info(
            f"🔧 {self.__str__()} Function Calling: remove_record_in_memory({text})"
        )
        await self.memory_manager.delete(text)
        return f"Remove {text} from memory.", False, False

    async def update_record_in_memory(
        self, text: str, new_text: str
    ) -> Tuple[str, bool, bool]:
        logging.info(
            f"🔧 {self.__str__()} Function Calling: update_record_in_memory({text}, {new_text})"
        )
        await self.memory_manager.update(text, new_text)
        return f"Update {text} to {new_text}.", False, False

    @abc.abstractmethod
    async def __call__(self, *args, **kwargs) -> Any:
        pass

    @abc.abstractmethod
    def __str__(self) -> str:
        pass
