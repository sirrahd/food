# Create your views here.
import json
from django.shortcuts import get_object_or_404
from django.http import HttpResponseServerError, HttpResponse
from accounts.models import Account

def debuginfo(request):
    id = request.GET.get('id', '')
    account = get_object_or_404(Account, pk=id)
    response = {'id': account.id, 'auth_code': account.auth_code, 'refresh_token': account.refresh_token, 'access_token': account.access_token, 'access_token_expiration': account.access_token_expiration.isoformat()}
    return HttpResponse(json.JSONEncoder(indent=10).encode(response), content_type = 'text/plain')

def debugcart(request):
    id = request.GET.get('id', '')
    account = get_object_or_404(Account, pk=id)
    response = account.testCart()
    return HttpResponse(json.JSONEncoder(indent=10).encode(response), content_type = 'text/plain')

def index(request):
    id = request.GET.get('id', '')
    account = get_object_or_404(Account, pk=id)
    user = account.get_user_info()
    response = {'username': user.username, 'email': user.email, 'first_name': user.first_name, 'last_name': user.last_name}
    return #HttpResponse(json.JSONEncoder(indent=10).encode(response), content_type = 'text/plain')

def create(request):
    account = Account()
    url = account.create()
    response = {'url': url, 'id': account.id}
    return HttpResponse(json.JSONEncoder(indent=10).encode(response), content_type = 'text/plain')

def authorize(request):
    error = request.GET.get('error', '')
    code = request.GET.get('code', '')
    state = request.GET.get('state', '')

    account = get_object_or_404(Account, pk=state)

    if error:
        account.delete()
        return HttpResponseServerError
    else:
        account.get_tokens(code)

    return HttpResponse('authorize')
