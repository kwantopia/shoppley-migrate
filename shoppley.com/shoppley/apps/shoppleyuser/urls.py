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
	url(r'^customer/signup-success/$',direct_to_template,{"template": "shoppleyuser/customer_landing_page.html"},name="customer_landing_page"),
	url(r'^merchant/signup-success/$',direct_to_template,{"template": "shoppleyuser/merchant_landing_page.html"},name="merchant_landing_page"),
	url(r'customer/offer-frequency-set/$',offer_frequency_set, name ="offer_frequency_set"),
)



