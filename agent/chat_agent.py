from datetime import datetime, timedelta
from agent.base_agent import BaseAgent
from schedule.views import get_day_event
from user.models import User
from typing import Tuple
import logging
import json
import matplotlib.pyplot as plt
from event.models import Event
import base64


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
    
    def send_schedule(self, date: str) -> Tuple[Tuple, bool, bool]:
        logging.info(f"🔧 {self.__str__()} Function Calling: send_schedule({date})")
        events = []
        for i in range(7):
            _date = datetime.strptime(date, "%Y-%m-%d").date()
            _date += timedelta(days=i)
            r = get_day_event(_date, self.user)
            events.extend([e for e in r])

        def cal_y(time: datetime.time, height_total):
            print(time.hour, time.minute, time.second)
            hour = time.hour + time.minute / 60 + time.second / 3600
            print(hour)
            return height_total * (1 - hour / 24)

        def draw_a_schedule(events: list[Event], path = ""):
            # plt.rcParams['font.sans-serif'] = ['SimHei']
            # plt.rcParams['axes.unicode_minus'] = False 
            # rcParams['font.family'] = 'SimHei'
            days = 7
            total_height = 24
            # 创建一个图形
            fig, ax = plt.subplots()

            # 获取当前日期
            current_date = datetime.now().date()
            date2 = current_date + timedelta(days=days)
            for event in events:
                if event.dateStart >= current_date and event.dateStart < date2:
                    if(event.dateStart == event.dateEnd):
                        x = (event.dateStart - current_date).days
                        width = 1
                        y = cal_y(event.timeStart, total_height)
                        height = cal_y(event.timeEnd, total_height) - cal_y(event.timeStart, total_height)
                        # print(x, width, y, height)
                        rectangle = plt.Rectangle((x, y), width, height, edgecolor='black', facecolor='cyan')

                        # 将方块添加到图形中
                        ax.add_patch(rectangle)
                        chinese_text = event.title

                        # 在方块中间添加中文字符
                        text_x = x + width / 2
                        text_y = y + height / 2

                        # 添加中文文本
                        ax.text(text_x, text_y, chinese_text, ha='center', va='center')

            # 设置坐标轴范围
            ax.set_xlim(0, days)
            ax.set_ylim(0, total_height)

            # 设置坐标轴标签
            ax.set_xlabel('date')
            ax.set_ylabel('hour')
            ax.set_yticks(range(0, 25, 4))
            plt.gca().invert_yaxis()
            x_tick_labels = [""]
            date0 = current_date.strftime('%m/%d')
            for i in range(7):
                x_tick_labels.append((str)(current_date + timedelta(days=i)))
            ax.set_xticklabels(x_tick_labels, rotation=-10, ha='right')

            # 设置图形标题
            ax.set_title('schedulers in a week')

            # 显示图形
            img_path = path + f"/{(str)(datetime.now())}.png"
            plt.savefig(img_path)
            return img_path

        def encode_image_to_base64(file_path):
            with open(file_path, "rb") as image_file:   
                image_data = image_file.read()
                base64_encoded = base64.b64encode(image_data).decode("utf-8")
            return base64_encoded

        file_path = draw_a_schedule(events)
        base64_encoded_image = encode_image_to_base64(file_path)
        return (base64_encoded_image,), True, False
    
    def get_web_url(self) -> Tuple[str, bool, bool]:
        logging.info(f"🔧 {self.__str__()} Function Calling: get_web_url()")
        token = self.user.generate_temp_token()
        return f"todo.yuan.cf/login?token={token}", True, False

    def __str__(self) -> str:
        return "ChatAgent"
