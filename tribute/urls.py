from django.urls import path
from . import views

urlpatterns = [
    path('', views.for_reinhardt, name='for_reinhardt'),
]
