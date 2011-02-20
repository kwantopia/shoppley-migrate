from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from shoppleyuser.views import *
from shoppleyuser.forms import MerchantSignupForm

urlpatterns = patterns('',
	url(r'^merchant/signup/$', merchant_signup, name="merchant_signup"),
	(r'^validate/$', 'ajax_validation.views.validate', 
		{'form_class': MerchantSignupForm}, 'merchant_signup_form_validate'),
)



