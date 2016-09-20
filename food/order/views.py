import json
import time
from xml.sax.saxutils import unescape
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from order.models import Order
from accounts.models import Account
from django.http import Http404
from django.shortcuts import render

def html(request):
    id = request.GET.get('id', '')
    n = int(request.GET.get('n', '1'))
    address = request.GET.get('address', '1 Memorial Drive Cambridge MA 02142')
    debug = request.GET.get('debug', '')
    account = get_object_or_404(Account, pk=id)
    order = Order()
    try:
        response = order.get_order(account, n, debug, address)
    except:
        try:
            response = order.get_order(account, n, debug, address)
        except:
            try:
                response = order.get_order(account, n, debug, address)
            except:
                raise Http404
    
    order.save()
    response['order']['id'] = order.id

    menu_name = []
    for item in response['food']:
        if item['menu_name'] not in menu_name:
            menu_name.append(item['menu_name'])

    ordered_food = []
    for menu in menu_name:
        for item in response['food']:
            if item['menu_name'] == menu:
                item['extra_count'] = len(item['extras'])
                ordered_food.append(item)
    response['ordered_food'] = {}
    response['ordered_food']['menu'] = menu_name
    response['ordered_food']['food'] = ordered_food

    return render(request, 'index.html', response)

def create(request):
    id = request.GET.get('id', '')
    n = int(request.GET.get('n', '1'))
    address = request.GET.get('address', '1 Memorial Drive Cambridge MA 02142')
    debug = request.GET.get('debug', '')
    account = get_object_or_404(Account, pk=id)
    order = Order()
    try:
        response = order.get_order(account, n, debug, address)
    except:
        try:
            response = order.get_order(account, n, debug, address)
        except:
            try:
                response = order.get_order(account, n, debug, address)
            except:
                raise Http404
    
    order.save()
    response['order']['id'] = order.id

    if debug == '':
        return HttpResponse(unescape(json.dumps(response)), content_type = 'application/json')
    else:
        return HttpResponse(json.JSONEncoder(indent=10).encode(response), content_type = 'text/plain')
