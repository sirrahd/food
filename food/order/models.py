import json
import urllib
import urllib2
import httplib
import random
import time
import datetime
from django.utils.timezone import utc
from django.http import Http404
from django.db import models
from accounts.models import Account
from django.conf import settings

class Order(models.Model):
    restaurant_id = models.CharField(max_length=32)
    account = models.ForeignKey(Account)

    def get_order(self, account, n, debug = '', address='1 Memorial Drive, Cambridge, MA 02142'):
        self.account = account
        restaurant_info = self.select_restaurant(address);
        restaurant = restaurant_info['restaurant']
        address = restaurant_info['address']
        restaurant_response = {
                               'name': restaurant['summary']['name'],
                               'city': restaurant['location']['city'],
                               'phone': restaurant['summary']['phone'],
                               }
        self.restaurant_id = restaurant['id']
        self.clear_cart()
        food = self.select_food(self.restaurant_id, n)
        food_response = []
        for item in food:
            item_response = {}
            item_response['menu_id'] = item['menu_id']
            item_response['menu_name'] = item['menu_name']
            item_response['description'] = item['description']
            item_response['id'] = item['id']
            item_response['name'] = item['name']
            item_response['extras'] = []
            for extra in item['children']:
                selection = self.recursive_select_options(extra)
                if selection != []:
                    item_response['extras'].extend(self.recursive_select_options(extra))
            self.add_to_cart(item_response)
            food_response.append(item_response)

        if debug != '':
            response = {'food': food_response, 'restaurant': restaurant_response, 'order': self.get_cart(account, self.restaurant_id), 'debug': {'food': food, 'restaurant': restaurant}}
        else:
            response = {'food': food_response, 'restaurant': restaurant_response, 'order': self.get_cart(account, self.restaurant_id)}

        response['order']['address'] = address

        return response

    def get_cart(self, account, restaurant_id):
        req = urllib2.Request('https://api.delivery.com/customer/cart/' + restaurant_id, None, {'Authorization': account.access_token})
        response = urllib2.urlopen(req)
        js = response.readlines()
        js_object = json.loads(js[0])

        return js_object

    def recursive_select_options(self, item):
        extras = []
        if 'min_selection' in item:
            for i in range(int(item['min_selection'])):
                newitem = random.choice(item['children'])
                if 'min_selection' in newitem['children']:
                    extras = self.recursive_select_options(newitem['children'])
                extras.append({
                               'description': newitem['description'],
                               'id': newitem['id'],
                               'name': newitem['name'],
                               })

        return extras

    def add_to_cart(self, item):
        url = 'https://api.delivery.com/customer/cart/' + self.restaurant_id
        values = {'order_type': 'delivery',
                    'instructions': '',
                    'item': {'item_id': item['id'], 'item_qty': 1},
                    'client_id': settings.DELIVERY_CLIENT_ID}

        option_qty = {}
        for extra in item['extras']:
            option_qty[extra['id']] = 1

        if len(option_qty) > 0:
            values['item']['option_qty'] = option_qty

        data = json.dumps(values)
        req = urllib2.Request(url, data, {'Authorization': self.account.access_token, 'Content-Type': 'application/json'})
        response = urllib2.urlopen(req)
        js = response.readlines()

    def clear_cart(self):
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request('https://api.delivery.com/customer/cart/' + self.restaurant_id, data='{}')
        request.add_header('Authorization', self.account.access_token)
        request.add_header('Content-Type', 'application/json')
        request.get_method = lambda: 'DELETE'
        url = opener.open(request)

    def get_order_info(self, restaurant_id, food_ids):
        restaurant = get_restaurant(restaurant_id)

        return format_order_info(restaurant, food)

    def format_order_info(self, restaurant, food):
        return {'restaurant': restaurant, 'food': food}

    def get_restaurant(self, restaurant_id):
        return self.get_response('merchant/' + restaurant_id)

    def get_menu(self):
        return self.get_response('merchant/' + self.restaurant_id + '/menu')

    def select_restaurant(self, address):
        random.seed()

        response= self.get_response('merchant/search/delivery', 'address=' + address + '&merchant_type=R')

        valid_restaurants = []
        for restaurant in response['merchants']:
            if restaurant['ordering']['is_open'] == True:
                valid_restaurants.append(restaurant)
        
        restaurant = random.choice(valid_restaurants)

        response = {'restaurant': restaurant, 'address': response['search_address']}

        return response

    def select_food(self, restaurant_id, n):
        response = self.get_menu()

        food = []
        for i in range(n):
            for x in range(10):
                menu = self.select_menu(response)
                food_item = random.choice(menu['children'])
                if food_item['name'][0:4].lower() != 'add ':
                    food_item['menu_id'] = menu['id']
                    food_item['menu_name'] = menu['name']
                    food.append(food_item)
                    break
                if x == 4:
                    raise Http404

        return food

    def make_order(self, n):
        restaurant = self.select_restaurant()
        food = self.select_food(restaurant['id'], n)

        return self.format_order_info(restaurant, food)

    def get_response(self, request_uri, request_params = ''):
        search_url = 'http://api.delivery.com/' + request_uri + '?client_id=' + settings.DELIVERY_CLIENT_ID + '&' + request_params
        raw = urllib.urlopen(search_url, None, {'Authorization': self.account.access_token})
        js = raw.readlines()
        js_object = json.loads(js[0])

        return js_object

    def select_menu(self, response):

        menus = response['menu']
        valid_menu_names = [
                            'Rice Specials',
                            'Dosa',
                            'House Specialties',
                            'Subs',
                            'Wings',
                            'Pita Roll-Ups',
                            'Entree',
                            'Seafood'
                            'Sea food',
                            'Dinner',
                            'Lunch',
                            'Gyro',
                            'Contorni',
                            'Panini',
                            'Poultry',
                            'Chicken',
                            'Beef',
                            'Steak',
                            'Pasta',
                            'Lamb',
                            'Uttapam',
                            'Kathi',
                            'Idli',
                            'Tandoori',
                            'Goat',
                            'Wrap',
                            'Sandwich',
                            'Pizza',
                            'Insalata',
                            'From Boqueron, Puerto Rico',
                            'Primi',
                            'From The Mortar',
                            'House Specials',
                            'Fish',
                            'Mein',
                            'Foo Young',
                            'Chop Suey',
                            'Fried Rice',
                            'Totes',
                            'Nigiri',
                            'Maki',
                            'Sushi',
                            'Raw Bar',
                            'Vegetarian',
                            'Specialties',
                            'Burger',
                            'Taco',
                            'Burrito',
                            'Quesadilla',
                            'Plate',
                            ]

        invalid_menu_names = [
                              'Catering',
                              'Eco-Friendly',
                              ]
        
        valid_menus = []

        for menu in menus:
            if menu not in valid_menus:
                bad = False
                for badword in invalid_menu_names:
                    if badword.lower() in menu['name'].lower():
                        bad = True
                        break
                if bad == True:
                    continue

                for word in valid_menu_names:
                    if word.lower() in menu['name'].lower():
                        valid_menus.append(menu)
                        break

        if len(valid_menus) > 0:
            return random.choice(valid_menus)
        else:
            raise Http404

        