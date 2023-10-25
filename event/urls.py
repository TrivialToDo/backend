from django.urls import path
from . import views

urlpatterns = [
    path('<str:hash>', views.get_event, name='get_event'),
]