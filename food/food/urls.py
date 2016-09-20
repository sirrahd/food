from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'food.views.home', name='home'),
    # url(r'^food/', include('food.food.urls')),
    url(r'^accounts/', include('accounts.urls', namespace='accounts')),
    url(r'^order/', include('order.urls', namespace='order')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
