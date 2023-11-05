"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.middleware.csrf import get_token

from utils.utils_request import request_success

urlpatterns = [
    path('token', lambda req: request_success({"token": get_token(req)})),
    path('schedule/', include('schedule.urls')),
    path('event/', include('event.urls')),
    path('wechat/', include('wechat.urls')),
]
