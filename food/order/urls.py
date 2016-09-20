from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView

urlpatterns = patterns('',
    url(r'^create/$', 'order.views.create', name='create'),
    url(r'^html/$', 'order.views.html', name='html'),
)