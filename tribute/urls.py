from django.urls import path
from . import views

urlpatterns = [
    path('for_reinhardt/', views.for_reinhardt, name='for_reinhardt'),
]
