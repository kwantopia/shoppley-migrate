from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from shoppleyuser.views import *

urlpatterns = patterns('',
	url(r'^merchant/signup/$', merchant_signup, name="merchant_signup"),
)



