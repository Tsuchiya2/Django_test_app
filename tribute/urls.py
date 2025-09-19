# tribute/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # URL名は学習しやすさ重視でASCIIを推奨
    path("for_reinhardt/", views.for_reinhardt, name="for_reinhardt"),

    # ★どうしても「for_ラインハルト」をURLにしたい場合（動きます）
    # path("for_ラインハルト/", views.for_reinhardt, name="for_ラインハルト"),
]
