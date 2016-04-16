from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
import sys
import os

# Create your views here.

def hello(request):
    return HttpResponse("hello world")

def search(request):
    if 'q' in request.GET:
        message = request.GET['q']
        freq = open('studio/request.txt', 'w')
        freq.write(message + '\n')
        freq.close()
        os.system("./studio/check_serve");
        fres = open('studio/result.txt', 'r')
        strlist = fres.readlines()
        fres.close()
    else:
        message = 'Search for a tree'
        strlist = []
    return render_to_response('index.html', {'display': 'result', 'message': message, 'strlist': strlist})
