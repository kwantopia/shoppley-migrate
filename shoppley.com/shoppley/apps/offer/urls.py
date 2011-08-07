from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from offer.views import *

urlpatterns = patterns('',
  url(r'^$', offer_home, name="offer_home"),
	url(r'offers/$', customer_offer_home, name="customer_offer_home"),
	url(r'business-home/$', merchant_offer_home, name="merchant_offer_home"),
	url(r'^start/$', start_offer, name="start_offer"),
	url(r'^test/$', test_offer, name="test_offer"),
	
)


