import requests
from user.models import User
from config import config
from utils.utils_logger import get_logger


def send_message(user: User, _type: str, content: str):
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
    }
    cookies = {}

    try:
        resp = requests.post(
            f'{config.wechat_url}/send_msg',
            headers=headers,
            cookies=cookies,
            json={
                "id": user.wechat_id,
                "type": _type,
                "content": content
            }
        )
        return resp
    except Exception as e:
        get_logger().error("request wechat failed", e)
        return None
