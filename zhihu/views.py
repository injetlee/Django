from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from zhihu.models import User
from django.urls import reverse


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        query = User.objects.get(email=email)
        global username
        username = query.name
        if password == query.password:
            return HttpResponseRedirect(reverse('zhihu:index'))
    else:
        return render(request, 'zhihu/login.html')

    # return render(request, 'zhihu/login.html')


def reg(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        name = request.POST['name']
        query = User(email=email, password=password, name=name)
        query.save()
        return render(request, 'zhihu/login.html')
    else:
        return render(request, 'zhihu/reg.html')


def index(request):
    global username
    return render(request, 'zhihu/index.html', {'name': username})


# def get_username():
