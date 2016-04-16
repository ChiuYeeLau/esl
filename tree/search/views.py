from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse

# Create your views here.

def hello(request):
    return HttpResponse("hello world")

def search(request):
    return render_to_response('index.html', {'post': 'result'});
