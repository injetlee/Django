from django.conf.urls import url
from django.contrib.auth.views import login, logout
from zhihu import views
app_name = 'zhihu'
urlpatterns = [
    url(r'^$', views.login, name='login'),
    url(r'^login/', views.login, name='login'),
    url(r'^reg/', views.reg, name='reg'),
    url(r'^index/', views.index, name='index')
]
