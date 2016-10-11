from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from zhihu.models import Question, Comment, UserPersonal

from django.urls import reverse
from django.contrib.auth import authenticate, login as loginin, logout
from itsdangerous import URLSafeSerializer
from django.conf import settings as django_settings
from django.core.mail import EmailMultiAlternatives,  EmailMessage
from django.contrib import messages
from django.template import loader, Context
import threading


def run_thread(msg):
    msg.send()


def send_mail(subject, to, from_email, html_content):
    msg = EmailMessage(subject, html_content, from_email, to)
    # msg.attach_alternative(html_content, 'text/html')
    msg.content_subtype = "html"
    # msg.send()
    thr = threading.Thread(target=run_thread, args=(msg,))
    thr.start()
    return thr


def login(request):
    if request.method == 'POST':
        username = request.POST['email']
        password = request.POST['password']
        user_exist = User.objects.get(username=username)
        user = authenticate(username=username, password=password)
        if user is not None:
            loginin(request, user)
            #messages.add_message(request, messages.SUCCESS, '登录成功，体验愉快')
            return redirect(reverse('zhihu:index'))
        elif user_exist is not None and user is None:
            messages.add_message(request, messages.SUCCESS, '未激活')
            return redirect(reverse('zhihu:login'))
        else:
            return redirect(reverse('zhihu:reg'))
    else:
        return render(request, 'zhihu/login.html')


def logout_view(request):
    logout(request)
    return render(request, 'zhihu/login.html')


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
                   'token': request.build_absolute_uri(
                       reverse('zhihu:active', args=[token, ]))}
        t = loader.get_template('zhihu/email.html')
        html_content = t.render(Context(context))

        send_mail('草乎认证邮件', [email],
                  django_settings.EMAIL_HOST_USER, html_content)
        messages.add_message(request, messages.SUCCESS, '注册成功，请前往邮箱进行激活后登录')

        return redirect(reverse('zhihu:login'))
    else:
        return render(request, 'zhihu/reg.html')

import time as tt


def format_time(time):
    print(tt.strftime('%Y-%m-%d %H:%M:%S', time))
    return tt.strftime('%Y-%m-%d %H:%M:%S', time)


@login_required(login_url='/zhihu/login/')
def index(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            title = request.POST['title']
            content = request.POST['question']
            if title != '':
                user = User.objects.get(username=request.user.username)
                updatetime = format_time(tt.localtime())
                insert = user.question_set.create(
                    title=title, content=content, updatedate=updatetime)
                insert.save()
        username = request.user.username
        latest_question = Question.objects.order_by('id')[::-1]
        # print(latest_question[0].user.userpersonal.signature)
        context = {
            'latest_question': latest_question,
            'name': username,
        }
        return render(request, 'zhihu/index.html', context)
    else:
        messages.add_message(request, messages.SUCCESS, '激活成功，欢迎登录')
        return HttpResponseRedirect(reverse('zhihu:login'))


def active(request, token):
    try:
        username = token_confirm.confirm_token(token)
    except:
        username = token_confirm.remove_token(token)
        user = User.objects.filter(username)
        for i in user:
            user.delete()
        return render(request, 'zhihu/reg.html')

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, 'zhihu/reg.html')
    user.is_active = True
    user.save()
    messages.add_message(request, messages.SUCCESS, '激活成功，欢迎登录')
    return redirect(reverse('zhihu:login'))


class Token:

    def __init__(self, secret_key):
        self.secret_key = secret_key
        # self.email = email

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


def post_question(request, id):
    # if request.method == 'POST':
    #     title = request.POST['title']
    #     content = request.POST['question']
    #     if title != '':
    #         user = User.objects.get(username=request.user.username)
    #         updatetime = format_time(tt.localtime())
    #         insert = user.question_set.create(
    #             title=title, content=content, updatedate=updatetime)
    #         insert.save()
    #     return redirect(reverse('zhihu:index'))
    if request.method == 'POST':
        comment = request.POST['comment']
        user = User.objects.get(username=request.user.username)
        post = Question.objects.get(pk=id)
        query = Comment.objects.create(
            content=comment, user=user, question=post, updatedate=format_time(tt.localtime()))
    post = Question.objects.get(pk=id)
    answer_query = Comment.objects.filter(question=id).order_by('-updatedate')
    answer_quantity = answer_query.count()
    return render(request, 'zhihu/question.html', {'post': post, 'quantity': answer_quantity, 'answers': answer_query})


@login_required
def create_question(request):
    return render(request, 'zhihu/create_question.html')


@login_required
def personal(request):
    user_id = request.user.id
    query = User.objects.get(pk=user_id)
    # signature = query.userpersonal.signature
    # area = query.userpersonal.area

    if request.method == 'POST':
        personal_signature = request.POST['signature']
        personal_area = request.POST['area']
        sex = request.POST.get('sex', False)

        if user_id:
            #query = User.objects.get(pk=user_id)
            #validate_exists = UserPersonal.objects.get(user_id=user_id)
            if UserPersonal.objects.filter(user=query):
                validate_exists = UserPersonal.objects.filter(user=query)
                validate_exists.delete()
            temp = UserPersonal(signature=personal_signature,
                                user=query, area=personal_area, sex=sex)
            temp.save()
    signature = query.userpersonal.signature
    area = query.userpersonal.area
    sex = query.userpersonal.sex

    return render(request, 'zhihu/personal.html', {'signature': signature, 'area': area, 'sex': sex})


# @login_required
# def comment(request, id):
#     if request.method == 'POST':
#         comment = request.POST['comment']
#         user = User.objects.get(username=request.user.username)
#         post = Question.objects.get(pk=id)
#         query = Comment.objects.create(
#             content=comment, user=user, question=post, updatedate=format_time(tt.localtime()))
#     return render(request, 'zhihu/comment.html', {'id': id})
