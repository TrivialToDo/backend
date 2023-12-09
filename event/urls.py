from django.urls import path
from . import views

urlpatterns = [
    path('new', views.new_event, name='new_event'),
    path('modify', views.modify_event, name='modify_event'),
    path('<str:hash>', views.deal_event, name='deal_event'),
]
