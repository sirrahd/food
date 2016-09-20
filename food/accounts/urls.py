from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView

urlpatterns = patterns('',
    url(r'^$', 'accounts.views.index', name='index'),
    url(r'^create/$', 'accounts.views.create', name='create'),
    url(r'^authorize/$', 'accounts.views.authorize', name='authorize'),
    url(r'^debuginfo/$', 'accounts.views.debuginfo', name='debuginfo'),
    url(r'^debugcart/$', 'accounts.views.debugcart', name='debugcart'), 
)