from django.urls import path
from . import views

urlpatterns = [
    path('day/<str:_date>', views.get_day, name='get_day'),
    path('week/<str:_date>', views.get_week, name='get_week'),
    path('month/<str:_date>', views.get_month, name='get_month'),
]
