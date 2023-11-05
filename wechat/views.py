from django.views.decorators.http import require_http_methods

from utils.utils_request import request_success


# Create your views here.


@require_http_methods(['POST'])
def recv_msg(req):
    return request_success({
        "type": "text",
        "content": "hello world"
    })
