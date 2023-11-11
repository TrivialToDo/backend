import requests
from user.models import User


def send_message(user: User, _type: str, content: str):
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
    }
    cookies = {}

    return requests.post(
        'http://wechat/send_msg',
        headers=headers,
        cookies=cookies,
        data={
            "id": user.wechat_id,
            "type": _type,
            "content": content
        }
    )
