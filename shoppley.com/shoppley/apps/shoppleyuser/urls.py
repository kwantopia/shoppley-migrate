from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from shoppleyuser.views import *
from shoppleyuser.forms import MerchantSignupForm, CustomerSignupForm

urlpatterns = patterns('',
	url(r'^merchant/signup/$', merchant_signup, name="merchant_signup"),
	url(r'^customer/signup/$', customer_signup, name="customer_signup"),

	(r'^validate/$', 'ajax_validation.views.validate', 
		{'form_class': MerchantSignupForm}, 'merchant_signup_form_validate'),
	url(r'^login/$', login_modal, name="login_modal"),
	url(r'^account/profile/$', user_profile, name = "user_profile"),
	url(r'^customer/profile-settings/$', customer_profile, name="customer_profile"),
	url(r'^merchant/profile-settings/$', merchant_profile, name="merchant_profile"),
	url(r'^customer/profile-edit/$', customer_profile_edit, name="customer_profile_edit"),
	url(r'^merchant/profile-edit/$', merchant_profile_edit, name="merchant_profile_edit"),
	url(r'^customer/signup-success/$',direct_to_template,{"template": "shoppleyuser/customer_landing_page.html"},name="customer_landing_page"),
	url(r'^merchant/signup-success/$',direct_to_template,{"template": "shoppleyuser/merchant_landing_page.html"},name="merchant_landing_page"),
	url(r'customer/offer-frequency-set/$',offer_frequency_set, name ="offer_frequency_set"),

	url(r'^customer/facebox/signup/$', direct_to_template, {"template": "shoppleyuser/customer_signup_facebox.html", "extra_context": {"form": CustomerSignupForm}}, name="customer_signup_facebox"),
	url(r'^merchant/facebox/signup/$', direct_to_template, {"template": "shoppleyuser/merchant_signup_facebox.html", "extra_context": {"form": MerchantSignupForm}}, name="merchant_signup_facebox"),

	url(r'^post/shoppleyuser/timezone/$', set_user_timezone, name="set_user_timezone"),
	url(r'^post/shoppleyuser/latlon/$', set_user_latlon, name="set_user_latlon"),
	url(r'^fb-connect-init/$', fb_connect_init, name="fb_connect_init"),
	url(r'^fb-login/$', fb_login, name="fb_login"),
	url(r'^fb-connect-success/$', fb_connect_success, name="fb_connect_success"),
	url(r'^fb-extra-info/$', direct_to_template, {"template": "shoppleyuser/fb_extra_info_html"}, name="fb_extra_info"),
	url(r'^customer/zip-phone/$', fb_customer_extra_info, name="fb_customer_extra_info"),
	url(r'^merchant/biz-loc-phone/$', fb_merchant_extra_info, name="fb_merchant_extra_info"),

)



