from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from search.util import *
import sys
import os

# Create your views here.

def hello(request):
    return HttpResponse("hello world")

def search(request):
    if 'q' in request.GET:
        message = request.GET['q']
        strlist = get_query_db(message)
    else:
        message = 'Search for a tree'
        strlist = []
    return render_to_response('index.html', {'display': 'result', 'message': message, 'strlist': strlist})
