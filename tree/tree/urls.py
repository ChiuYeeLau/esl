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
    url(r'^search7/', search4, {'stype': 1}),
    url(r'^search8/', search4, {'stype': 2}),
    url(r'^search9/', search4, {'stype': 3}),
    url(r'^search10/', search4, {'stype': 4}),
    url(r'^syntaxtree/', get_tree),
]
