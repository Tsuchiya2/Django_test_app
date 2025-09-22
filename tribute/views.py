from django.shortcuts import render # 変更

def for_reinhardt(request):
    return render(request, 'tribute/for_reinhardt.html') # 変更
