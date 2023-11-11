from django.urls import path
from . import views

urlpatterns = [
    path('<str:hash>', views.deal_event, name='deal_event'),
]
