import json
import hashlib
import uuid
import urllib
import urllib2
import datetime
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.
class Account(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    auth_code = models.CharField(max_length=64, null=True)
    refresh_token = models.CharField(max_length=64, null=True)
    access_token = models.CharField(max_length=64, null=True)
    access_token_expiration = models.DateTimeField(null=True)
    user = models.ForeignKey(User, null=True)

    def testCart(self):
        url = 'https://api.delivery.com/customer/cart/77670'
        values = {'order_type': 'delivery',
                    'instructions': 'don\'t deliver',
                    'item': {'item_id': 'N228','item_qty': 1},
                    'client_id': settings.DELIVERY_CLIENT_ID}

        data = urllib.urlencode(values)
        data = json.dumps(values)
        req = urllib2.Request(url, data, {'Authorization': 'RslGHE4NMKDe6tMXxDI1zmh5XoZ8OsMifJe8rMnl '})
        response = urllib2.urlopen(req)
        js = response.readlines()
        return json.loads(js[0])


    def create(self):
        self.id = hashlib.sha1(str(uuid.uuid4())).hexdigest()
        self.save()
        return self.oauth_authorize_request()

    def oauth_authorize_request(self):
        return 'https://api.delivery.com/third_party/authorize?client_id=' + settings.DELIVERY_CLIENT_ID + '&redirect_uri=' + settings.URI_ROOT + 'accounts/authorize&response_type=code&scope=global&state=' + self.id

    def get_tokens(self, auth_code):
        self.auth_code = auth_code
        self.save()

        url = 'https://api.delivery.com/third_party/access_token'
        values = {'client_id': settings.DELIVERY_CLIENT_ID,
                    'redirect_uri': settings.URI_ROOT + 'accounts/authorize',
                    'grant_type': 'authorization_code',
                    'client_secret': settings.DELIVERY_SECRET,
                    'code': self.auth_code}

        data = urllib.urlencode(values)
        data = json.dumps(values)
        req = urllib2.Request(url, data, {'Content-Type': 'application/json', 'Content-Length': len(data)})
        response = urllib2.urlopen(req)
        js = response.readlines()
        js_object = json.loads(js[0])

        self.access_token = js_object['access_token']
        self.refresh_token = js_object['refresh_token']
        self.access_token_expiration = datetime.datetime.utcfromtimestamp(js_object['expires'])
        self.save()

        self.get_user_info()
        
    def get_user_info(self):
        req = urllib2.Request('https://api.delivery.com/customer/account', None, {'Authorization': self.access_token})
        response = urllib2.urlopen(req)
        js = response.readlines()
        js_object = json.loads(js[0])
        user_web = js_object['user']

        try:
            user_db = User.objects.get(username=user_web['human_id'])
            user_db.email = user_web['email']
            user_db.first_name = user_web['first_name']
            user_db.last_name = user_web['last_name']
            user_db.save()
        except:
            user_db = User.objects.create(username=user_web['human_id'], 
                                          password='938v498w4vn89w4v',
                                          email=user_web['email'],
                                          first_name = user_web['first_name'],
                                          last_name = user_web['last_name'])

        return user_db
