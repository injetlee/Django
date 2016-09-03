from django.shortcuts import render, redirect

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User

from django.urls import reverse
from django.contrib.auth import authenticate, login as loginin
from itsdangerous import URLSafeSerializer
from django.conf import settings as django_settings
from django.core.mail import EmailMultiAlternatives,  EmailMessage
from django.contrib import messages
from django.template import loader, Context


def login(request):
    if request.method == 'POST':
        username = request.POST['email']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user.is_authenticated():
            if user.is_active:
                loginin(request, user)
                messages.add_message(request, messages.SUCCESS, '登录成功，体验愉快')
                return redirect(reverse('zhihu:index'))
    else:
        return render(request, 'zhihu/login.html')

    # return render(request, 'zhihu/login.html')


def reg(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        username = request.POST['name']
        user_exist = User.objects.filter(username=username)

        if user_exist:
            messages.add_message(request, messages.ERROR, '用户名已经被注册')
            return render(request, 'zhihu/reg.html')

        query = User.objects.create_user(
            email=email, password=password, username=username)
        query.is_active = False
        query.save()
        token = token_confirm.generate_token(username)
        context = {'username': username,
                   'token': 'http://127.0.0.1:8000/zhihu/active/%s' % token, }
        t = loader.get_template('zhihu/email.html')
        html_content = t.render(Context(context))
        send_mail('caohu', [email], 'liyingjie26@126.com', html_content)
        messages.add_message(request, messages.SUCCESS, '注册成功，请前往邮箱进行激活后登录')

        return redirect(reverse('zhihu:login'))
    else:
        return render(request, 'zhihu/reg.html')


def index(request):
    if request.user.is_authenticated():
        username = request.user.username
        return render(request, 'zhihu/index.html', {'name': username})
    else:
        messages.add_message(request, messages.SUCCESS, '激活成功，欢迎登录')
        return HttpResponseRedirect(reverse('zhihu:login'))


# def active(request, token):
#     # try:
#     username = token_confirm.confirm_token(token)
#     # except:
#     #     username = token_confirm.remove_token(token)
#     #     user = User.objects.filter(username)
#     #     for i in user:
#     #         user.delete()
#     #     return render(request, 'zhihu/login.html')

#     # try:
#     user = User.objects.get(username=username)
#     # except User.DoesNotExist:
#     #     return render(request, 'zhihu/login.html')
#     user.is_active = True
#     user.save()
#     return redirect(reverse('zhihu:index'))


def active(request, token):
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
    return redirect(reverse('zhihu:index'))

    # def get_username():
# def active(request, token):
#     a = token
#     c = Token(django_settings.SECRET_KEY)
#     d = c.generate_token(a)
#     f = c.confirm_token(a)
#     #username = token_confirm.confirm_token(a)
#     #username = token_confirm.remove_token(token)
#     # print(username)
#     # user = User.objects.filter(username)
#     #     for i in user:
#     #         user.delete()
#     #     return render(request, 'zhihu/login.html')

#     # try:
#     #     user = User.objects.get(username=username)
#     # except User.DoesNotExist:
#     #     return render(request, 'zhihu/login.html')
#     # user.is_active = True
#     # user.save()
#     return render(request, 'zhihu/index.html', {'token': f})


class Token:

    def __init__(self, secret_key):
        self.secret_key = secret_key
        #self.email = email

    def generate_token(self, email):
        s = URLSafeSerializer(self.secret_key)
        token = s.dumps(email)
        return token

    def confirm_token(self, token):
        s = URLSafeSerializer(self.secret_key)
        result = s.loads(token)
        return result

    def remove_token(self, token):
        s = URLSafeSerializer(self.secret_key)
        return s.loads(token)

    # def remove_token(self, token):
token_confirm = Token(django_settings.SECRET_KEY)


def send_mail(subject, to, from_email, html_content):
    msg = EmailMessage(subject, html_content, from_email, to)
    #msg.attach_alternative(html_content, 'text/html')
    msg.content_subtype = "html"
    msg.send()
