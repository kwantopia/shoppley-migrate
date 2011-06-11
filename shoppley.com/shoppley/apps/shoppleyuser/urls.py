from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from shoppleyuser.views import *
from shoppleyuser.forms import MerchantSignupForm

urlpatterns = patterns('',
	url(r'^merchant/signup/$', merchant_signup, name="merchant_signup"),
	url(r'^customer/signup/$', customer_signup, name="customer_signup"),
	url(r'^customer/betasubscribe$',customer_beta_subscribe, name="customer_beta_subscribe"),
	(r'^validate/$', 'ajax_validation.views.validate', 
		{'form_class': MerchantSignupForm}, 'merchant_signup_form_validate'),
	url(r'^login/$', login_modal, name="login_modal"),
)



