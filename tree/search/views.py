# from django.shortcuts import render
# from django.shortcuts import render_to_response
from django.http import HttpResponse, JsonResponse
from search.util import get_query_inter, get_parse
from search.qtree import get_qtree_inter
import json

# Create your views here.


def hello(request):
    return HttpResponse("hello world")

'''
def search(request):
    if 'q' in request.GET:
        message = request.GET['q']
        strlist = get_query_db(message)
    else:
        message = 'Search for a tree'
        strlist = []
    return render_to_response('index.html', {'display': 'result', 'message': message, 'strlist': strlist})
'''


def search2(request):
    if request.method == 'GET':
        message = request.GET.get('sentence', '')
        keys = request.GET.get('word_pos', '')
        key = [int(ele) for ele in keys.split(' ') if len(ele) > 0]
        if message != '':
            strlist = get_query_inter(message, key)
        else:
            strlist = []
    else:
        strlist = []
    # message = 'a computer database'
    # key = [0, 1, 2]
    # strlist = get_query_inter(message, key)
    return HttpResponse(json.dumps(strlist))
    # return render_to_response('search.html', {'output': strlist})


def search3(request):
    if request.method == 'GET':
        message = request.GET.get('sentence', '')
        keys = request.GET.get('word_pos', '')
        key = [int(ele) for ele in keys.split(' ') if len(ele) > 0]
        if message != '':
            strlist = get_qtree_inter(message, key)
        else:
            strlist = {}
    else:
        strlist = {}
    return JsonResponse(strlist)


def get_tree(request):
    trees = {}
    if request.method == 'GET':
        message = request.GET.get('tree', '')
        if message != '':
            trees = get_parse(message)
    return JsonResponse(trees)
