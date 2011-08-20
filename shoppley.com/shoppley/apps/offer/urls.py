from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from offer.views import *

urlpatterns = patterns('',
  url(r'^$', offer_home, name="offer_home"),
	url(r'offers/$', customer_offer_home, name="customer_offer_home"),
	url(r'business-home/$', merchant_offer_home, name="merchant_offer_home"),
	url(r'offer/(?P<offer_id>\d+)/$', customer_offer, name="customer_offer"),
	url(r'sendme/(?P<offer_id>\d+)/$', customer_offer_sendme, name="customer_offer_sendme"),
	url(r'business-offer/(?P<offer_id>\d+)/$', merchant_offer, name="merchant_offer"),
	url(r'admin-start/(?P<merchant_id>\d+)/$', admin_start_offer, name="admin_start_offer"),
	url(r'search-merchant/$', search_merchant, name="search_merchant"),
	url(r'^start/$', start_offer, name="start_offer"),
	url(r'^test/$', test_offer, name="test_offer"),
	url(r'^start-offer/$', merchant_start_offer, name="merchant_start_offer"),	

	
)


