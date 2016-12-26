"""tree URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from search.views import hello, search2, search3, search4, get_tree

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^hello/', hello),
    # url(r'^search/', search),
    url(r'^search2/', search2),
    url(r'^search3/', search3, {'ctype': 0}),
    url(r'^search4/', search3, {'ctype': 1}),
    url(r'^search5/', search3, {'ctype': 2}),
    url(r'^search6/', search4, {'stype': 0}),
    url(r'^searchc0/', search4, {'stype': 1}),
    url(r'^searchc1/', search4, {'stype': 2}),
    url(r'^searchf0/', search4, {'stype': 3}),
    url(r'^searchf1/', search4, {'stype': 4}),
    url(r'^searchff0/', search4, {'stype': 5}),
    url(r'^searchff1/', search4, {'stype': 6}),
    url(r'^searchfm0/', search4, {'stype': 7}),
    url(r'^searchfm1/', search4, {'stype': 8}),
    url(r'^syntaxtree/', get_tree),
]
