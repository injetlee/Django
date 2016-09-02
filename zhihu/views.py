from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User

from django.urls import reverse
from django.contrib.auth import authenticate, login as loginin
from itsdangerous import URLSafeSerializer
from django.conf import settings as django_settings
from django.core.mail import send_mail
from django.contrib import messages


def login(request):
    if request.method == 'POST':
        username = request.POST['email']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user.is_authenticated():
            if user.is_active:
                loginin(request, user)
        return HttpResponseRedirect(reverse('zhihu:index'))
    else:
        return render(request, 'zhihu/login.html')

    # return render(request, 'zhihu/login.html')


def reg(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        username = request.POST['name']
        query = User.objects.create_user(
            email=email, password=password, username=username)
        #query.is_active = False
        query.save()
        send_mail('caohu', 'hello to caohu', 'liyingjie26@126.com',
                  [email], fail_silently=False,)
        # messages.add_message(request, messages.INFO, 'success helo')

        return HttpResponseRedirect(reverse('zhihu:login'))
    else:
        return render(request, 'zhihu/reg.html')


def index(request):
    if request.user.is_authenticated():
        username = request.user.username
        return render(request, 'zhihu/index.html', {'name': username})
    else:
        return HttpResponseRedirect(reverse('zhihu:login'))


def active(token):
    try:
        username = token_confirm.confirm_token(token)
    except:
        username = token_confirm.remove_token(token)
        user = User.objects.filter(username)
        for i in user:
            user.delete()
        return render(request, 'zhihu/login.html')

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, 'zhihu/login.html')
    user.is_active = True
    user.save()
    return render(request, 'zhihu/index.html')

    # def get_username():


class Token:

    def __init__(self, secret_key):
        self.secret_key = secret_key
        #self.email = email

    def generate_token(self):
        s = URLSafeSerializer(secret_key)
        token = s.dump(email)
        return token

    def confirm_token(self, token, expiration=3600):
        s = URLSafeSerializer(secret_key)
        result = s.loads(token, max_age=expiration)
        return result

    def remove_token(self, token):
        s = URLSafeSerializer(secret_key)
        return s.loads(token)

    # def remove_token(self, token):
token_confirm = Token(django_settings.SECRET_KEY)
