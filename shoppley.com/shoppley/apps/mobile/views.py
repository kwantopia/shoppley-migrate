# Create your views here.

import django
if django.VERSION[1] == 1:
	from django.contrib.csrf.middleware import csrf_exempt
else:
	from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.views.decorators.cache import cache_control, never_cache
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext, string_concat
from django.contrib.auth.models import User

if "mailer" in settings.INSTALLED_APPS:
    from mailer import send_mail
else:
    from django.core.mail import send_mail

from common.helpers import JSONHttpResponse, JSHttpResponse
from shoppleyuser.utils import sms_notify
from shoppleyuser.models import ZipCode, Merchant, Customer

# for generating random password
import random, string

@csrf_exempt
def mobile_login(request):
	data = {}

	email = request.POST['email'].lower()
	password = request.POST['password']
	user = authenticate(username=email, password=password)
	if user is not None:
		login(request, user)
		#logger.debug( "User %s authenticated and logged in"%email )
		data["result"] = 1
		return JSONHttpResponse(data)	 
	else:	
		data["result"] = -1
		return JSONHttpResponse(data)

@csrf_exempt
@login_required
def mobile_logout(request):
	data = {}
	logout(request)
	data["result"] = 1 
	return JSONHttpResponse(data)	

@csrf_exempt
def register_customer(request):
	data = {}
	
	# input parameters
	email = request.POST['email'].lower()
	phone = request.POST['phone']	
	zipcode = request.POST['zipcode']
	
	# need to clean up phone

	if not ZipCode.objects.filter(code=zipcode).exists():
		# ERROR: zip code is invalid
		data["result"] = "-2"
		return JSONHttpResponse(data)	
	else:
		zipcode_obj = ZipCode.objects.get(code=zipcode)

	u, created = User.objects.get_or_create(username=email, email=email)
	if created:
		s = string.lowercase+string.digits
		rand_passwd = ''.join(random.sample(s,6))
		u.set_password(rand_passwd)	
		u.save()
		# create customer information
		c = Customer(user=u, zipcode=zipcode_obj, phone=phone)
		c.save()

		# send a text message and e-mail with random password
		message = _("Here's your temporary password: %(password)s.  Please login to http://shoppley.com and update your password.") %{ "password": rand_passwd }
		recipients = [email]
		send_mail("Welcome to Shoppley", message, settings.DEFAULT_FROM_EMAIL, recipients)  
		txt_msg = _("%(password)s is temporary password from Shoppley") % { "password": rand_passwd }
		#sms_notify(phone, txt_msg)
	else:
		# ERROR: User exists, ask user to login with their password 
		data["result"] = "-1"
		return JSONHttpResponse(data)	

	# you can start viewing offers	
	user = authenticate(username=email, password=rand_passwd)
	if user is not None:
		login(request, user)
		#logger.debug( "User %s authenticated and logged in"%email )
		data["result"] = 1
		return JSONHttpResponse(data)	 
	else:
		# ERROR: problem authenticating user
		data["result"] = "-3"
		return JSONHttpResponse(data)
			


@csrf_exempt
@login_required
def offers_current(request):
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def offers_redeemed(request):
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def offer_forward(request):
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def offer_feedback(request):
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def offer_rate(request):
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def offer_rate(request):
	data = {}
	return JSONHttpResponse(data)	


#####################################
# Merchant mobile API
#####################################

@csrf_exempt
def register_merchant(request):
	data = {}
	# input parameters
	business_name = request.POST['business']
	email = request.POST['email'].lower()
	phone = request.POST['phone']	
	zipcode = request.POST['zipcode']
	
	# need to clean up phone

	if not ZipCode.objects.filter(code=zipcode).exists():
		# ERROR: zip code is invalid
		data["result"] = "-2"
		return JSONHttpResponse(data)	
	else:
		zipcode_obj = ZipCode.objects.get(code=zipcode)

	u, created = User.objects.get_or_create(username=email, email=email)
	if created:
		s = string.lowercase+string.digits
		rand_passwd = ''.join(random.sample(s,6))
		u.set_password(rand_passwd)	
		u.save()
		# create customer information
		c = Merchant(user=u, zipcode=zipcode_obj, phone=phone, business_name=business_name)
		# TODO: handle same business name? Possibly no need to
		c.save()

		# send a text message and e-mail with random password
		message = _("Here's your temporary password: %(password)s.  Please login to http://shoppley.com and update your password and you will be given free points to start sending Shoppley offers.") %{ "password": rand_passwd }
		recipients = [email]
		send_mail("Welcome to Shoppley", message, settings.DEFAULT_FROM_EMAIL, recipients)  
		txt_msg = _("%(password)s is temporary password from Shoppley") % { "password": rand_passwd }
		#sms_notify(phone, txt_msg)
	else:
		# ERROR: User exists, ask user to login with their password 
		data["result"] = "-1"
		return JSONHttpResponse(data)	

	# you can start viewing offers	
	user = authenticate(username=email, password=rand_passwd)
	if user is not None:
		login(request, user)
		#logger.debug( "User %s authenticated and logged in"%email )
		data["result"] = 1
		return JSONHttpResponse(data)	 
	else:
		# ERROR: problem authenticating user
		data["result"] = "-3"
		return JSONHttpResponse(data)


@csrf_exempt
@login_required
def splash_view(request):
	data = {}
	return JSONHttpResponse(data)	
	
	
@csrf_exempt
@login_required
def offers_active(request):
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def offer_start(request):
	data = {}
	data["offer_id"] = 1
	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def offer_send_more(request, offer_id):
	data = {}
	data["offer_id"] = 2
	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def offer_restart(request):
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def offer_redeem(request):
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def offers_past(request):
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def merchant_summary(request):
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def merchant_summary_viz(request):
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def offers_all(request):
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def point_summary(request):
	"""
		for the customer
	"""
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def point_offers(request):
	"""
		for the customer
	"""
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def point_offer(request, offer_id):
	"""
		for the customer, details of a point offer
	"""
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def point_offer_start(request):
	data = {}
	data["offer_id"] = 1
	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def point_offer_expire(request, offer_id):
	data = {}
	return JSONHttpResponse(data)	


