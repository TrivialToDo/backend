from django.urls import path
from . import views

urlpatterns = [
    path('receive_msg', views.recv_msg, name='receive_msg'),
]
