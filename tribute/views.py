# tribute/views.py
from django.shortcuts import render

def for_reinhardt(request):
    return render(request, "tribute/for_reinhardt.html")  # ← これでOK
