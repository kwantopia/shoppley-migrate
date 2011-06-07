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
from offer.models import Offer, OfferCode

# for generating random password
import random, string, time
from datetime import datetime

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
		sms_notify(phone, txt_msg)
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
	"""

		:param lat: current latitude
		:param lon: current longitude

		:rtype: JSON

		::

		# if user is not a customer
		{
			"result": -1
		}

	"""
	data = {}

	u = request.user
	if u.shoppleyuser.is_customer():

		# TODO: need to also dynamically generate offers based on current location
		# TODO: notify the merchant that another user has seen (update sent offers)
		# TODO: log the location it was seen from lat/lon, timestamp

		lat = request.POST.get("lat", None)
		lon = request.POST.get("lon", None)
			
		if lat == None or lon == None:
			# invalid location specified
			data["result"] = -2
			return JSONHttpResponse(data) 
			
			
		customer = u.shoppleyuser.customer
		user_offers = OfferCode.objects.filter(customer=customer, expiration_time__gt=datetime.now())
		data["num_offers"] = user_offers.count()
		data["offers"] = []

		#"expiration": str(time.mktime(o.expiration_time.timetuple())),
		for o in user_offers:
			data["offers"].append(o.offer_detail())	
		data["result"] = 1
	else:
		data["result"] = -1
	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def offers_current_filter(request):
	"""
		Returns a filtered version by filtering to a reduced set of those in current location
	"""
	data = {}

	u = request.user
	if u.shoppleyuser.is_customer():

		# TODO: need to also dynamically generate offers based on current location
		# TODO: notify the merchant that another user has seen (update sent offers)
		# TODO: log the location it was seen from lat/lon, timestamp

		lat = request.POST.get("lat", None)
		lon = request.POST.get("lon", None)
			
		if lat == None or lon == None:
			# invalid location specified
			data["result"] = -2
			return JSONHttpResponse(data) 
			
		customer = u.shoppleyuser.customer
		# need to narrow this query to just return those very close to lat, lon
		user_offers = OfferCode.objects.filter(customer=customer, expiration_time__gt=datetime.now())
		data["num_offers"] = user_offers.count()
		data["offers"] = []

		#"expiration": str(time.mktime(o.expiration_time.timetuple())),
		for o in user_offers:
			data["offers"].append(o.offer_detail())	
		data["result"] = 1
	else:
		data["result"] = -1
	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def offers_redeemed(request):
	data = {}

	u = request.user
	if u.shoppleyuser.is_customer():

		customer = u.shoppleyuser.customer
		# need to narrow this query to just return those very close to lat, lon
		user_offers = OfferCode.objects.filter(customer=customer).exclude(redeem_time__isnull=True)
		data["num_offers"] = user_offers.count()
		data["offers"] = []
		for o in user_offers:
			data["offers"].append( o.offer_detail() )	
	else:
		data["result"] = -1

	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def offer_forward(request):
	"""
		:param offer_code: the code that is forwarded
		:param phones: list of phone numbers
		:param note: a note for the friend

	"""
	data = {}

	u = request.user
	customer = u.shoppleyuser.customer

	offer_code = request.POST.get("offer_code", None)
	phones = request.POST.getlist("phones")
	notes = request.POST.get("note", "")
	if offer_code and len(phones) > 0:
		if OfferCode.objects.filter(code__iexact=offer_code).exists():
			original_code = OfferCode.objects.filter(code__iexact=offer_code)[0]
			offer = original_code.offer
			for phone in phones:
				new_code, random_pw = offer.gen_forward_offercode(original_code, phone)
				# text the user the user name and password

				customer_msg = _("%(code)s: %(customer)s has forwarded you this offer:\n - merchant: %(merchant)s\n - expiration: %(expiration)s\n - description: %(description)s\n - deal: %(dollar_off)s off\nPlease use this code %(code)s to redeem the offer.\n")%{
						"customer": customer,
						"merchant": offer.merchant,
						"expiration": original_code.expiration_time,
						"description": offer.description,
						"dollar_off": offer.dollar_off,
						"code": new_code.code,
						}
				#TODO: if the personal do not mind receiving txt
				sms_notify(phone,customer_msg)

				if random_pw:
					new_customer = new_code.customer
					#print "created a customer for %s" % friend_num
					account_msg = _("Welcome to Shoppley! Here is your shoppley.com login info:\n - username: %(name)s\n - password: %(password)s")%{"name":new_customer.user.username,"password":random_pw,}
					sms_notify(phone,account_msg)

			forwarder_msg= _('Offer by "%s" was forwarded to ') % offer_code
			forwarder_msg= forwarder_msg+ ''.join([str(i)+' ' for i in phones]) + "\nYou will receive points when they redeem their offers."
			data["confirm_msg"] = forwarder_msg 
			data["result"] = 1
		else:
			# ERROR: offer code is invalid
			data["result"] = -2
	else:
		# ERROR: no offer code POSTed
		data["result"] = -1

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
		data["result"] = -2
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
		data["result"] = -1
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
		data["result"] = -3
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
def customer_point_summary(request):
	"""
		for the customer
	"""
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def customer_point_offers(request):
	"""
		for the customer
	"""
	data = {}
	return JSONHttpResponse(data)	


@csrf_exempt
@login_required
def point_offers_active(request):
	data = {}
	data["offer_id"] = 1
	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def point_offers_past(request):
	data = {}
	data["offer_id"] = 1
	return JSONHttpResponse(data)	


@csrf_exempt
@login_required
def point_offer_start(request):
	data = {}
	data["offer_id"] = 1
	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def point_offer_restart(request):
	data = {}
	data["offer_id"] = 1
	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def point_offer_expire(request, offer_id):
	data = {}
	return JSONHttpResponse(data)	


