from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from zhihu.models import User
from django.urls import reverse


def login(request):
    if request.POST:
        email = request.POST['email']
        password = request.POST['password']
        query = User.objects.get(email=email)
        if password == query.password:
            return render(request, 'zhihu/index.html')
        else:
            return render(request, 'zhihu/login.html')

    return render(request, 'zhihu/login.html')


def reg(request):
    if request.POST:
        email = request.POST['email']
        password = request.POST['password']
        query = User(email=email, password=password)
        query.save()
        return render(request, 'zhihu/login.html')
    else:
        return render(request, 'zhihu/reg.html')


def index(request):
    return render(request, 'zhihu/index.html')
