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
from shoppleyuser.utils import sms_notify, parse_phone_number
from shoppleyuser.models import ZipCode, Merchant, Customer
from offer.models import Offer, OfferCode

# for generating random password
import random, string, time
from datetime import datetime, timedelta

SMS_DEBUG = True

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
		data["result_msg"] = "Login successful."
		return JSONHttpResponse(data)	 
	else:	
		data["result"] = -1
		data["result_msg"] = "Wrong email/password."
		return JSONHttpResponse(data)

@csrf_exempt
@login_required
def mobile_logout(request):
	data = {}
	logout(request)
	data["result"] = 1 
	data["result_msg"] = "Logout successful."
	return JSONHttpResponse(data)	

@csrf_exempt
def register_customer(request):
	data = {}
	
	# input parameters
	email = request.POST['email'].lower()
	phone = parse_phone_number(request.POST['phone'])
	zipcode = request.POST['zipcode']
	
	# need to clean up phone

	if not ZipCode.objects.filter(code=zipcode).exists():
		# ERROR: zip code is invalid
		data["result"] = -2
		data["result_msg"] = "Zip Code is invalid or not in the system."
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
		message = _("Here's your temporary password: %(password)s.	Please login to http://shoppley.com and update your password.") %{ "password": rand_passwd }
		recipients = [email]
		send_mail("Welcome to Shoppley", message, settings.DEFAULT_FROM_EMAIL, recipients)  
		txt_msg = _("%(password)s is temporary password from Shoppley") % { "password": rand_passwd }
		sms_notify(phone, txt_msg, SMS_DEBUG)
	else:
		# ERROR: User exists, ask user to login with their password 
		data["result"] = -1
		data["result_msg"] = "User already exists so you should login with their password."
		return JSONHttpResponse(data)	

	# you can start viewing offers	
	user = authenticate(username=email, password=rand_passwd)
	if user is not None:
		login(request, user)
		#logger.debug( "User %s authenticated and logged in"%email )
		data["result"] = 1
		data["result_msg"] = "User registered and authenticated successfully."
		return JSONHttpResponse(data)	 
	else:
		# ERROR: problem authenticating user
		data["result"] = -3
		data["result_msg"] = "Authentication error, possibly the user is not activated."
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
			data["result_msg"] = "No latitude and longitude specified."
			return JSONHttpResponse(data) 
			
			
		customer = u.shoppleyuser.customer
		user_offers = OfferCode.objects.filter(customer=customer, expiration_time__gt=datetime.now())
		data["num_offers"] = user_offers.count()
		data["offers"] = []

		#"expiration": str(time.mktime(o.expiration_time.timetuple())),
		for o in user_offers:
			data["offers"].append(o.offer_detail())	
		data["result"] = 1
		data["result_msg"] = "Returning offer details."
	else:
		data["result"] = -1
		data["result_msg"] = "User is not a customer."
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
			data["result_msg"] = "No latitude and longitude specified."
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
		data["result_msg"] = "Returning offer details."
	else:
		data["result"] = -1
		data["result_msg"] = "User is not a customer."
	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def offers_redeemed(request):
	data = {}

	u = request.user
	if u.shoppleyuser.is_customer():

		customer = u.shoppleyuser.customer
		user_offers = OfferCode.objects.filter(customer=customer).exclude(redeem_time__isnull=True)
		data["num_offers"] = user_offers.count()
		data["offers"] = []
		for o in user_offers:
			data["offers"].append( o.offer_redeemed() )	

		data["result"] = 1
		data["result_msg"] = "Returning redeemed offers."
	else:
		data["result"] = -1
		data["result_msg"] = "User is not a customer."

	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def offers_expired(request):
	"""
		Offers that expired and haven't been redeemed

		Future use: to indicate that they would like offers like this
	"""
	data = {}

	u = request.user
	if u.shoppleyuser.is_customer():

		customer = u.shoppleyuser.customer
		user_offers = OfferCode.objects.filter(customer=customer, expiration_time__lt=datetime.now(), redeem_time__isnull=True)

		data["num_offers"] = user_offers.count()
		data["offers"] = []
		for o in user_offers:
			data["offers"].append( o.offer_detail() )	

		data["result"] = 1
		data["result_msg"] = "Returning expired offers that have not been redeemed."
	else:
		data["result"] = -1
		data["result_msg"] = "User is not a customer."

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
				sms_notify(phone,customer_msg, SMS_DEBUG)

				if random_pw:
					new_customer = new_code.customer
					#print "created a customer for %s" % friend_num
					account_msg = _("Welcome to Shoppley! Here is your shoppley.com login info:\n - username: %(name)s\n - password: %(password)s")%{"name":new_customer.user.username,"password":random_pw,}
					sms_notify(phone,account_msg, SMS_DEBUG)

			forwarder_msg= _('Offer by "%s" was forwarded to ') % offer_code
			forwarder_msg= forwarder_msg+ ''.join([str(i)+' ' for i in phones]) + "\nYou will receive points when they redeem their offers."
			data["confirm_msg"] = forwarder_msg 
			data["result"] = 1
			data["result_msg"] = "Offers have been forwarded."
		else:
			# ERROR: offer code is invalid
			data["result"] = -2
			data["result_msg"] = "Offer code is invalid."
	else:
		# ERROR: no offer code POSTed
		data["result"] = -1
		data["result_msg"] = "Offer code has not been specified in POST parameter."

	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def offer_feedback(request):
	"""
		Provide feedback regarding a used offer
	"""
	data = {}

	offer_code_id = request.POST["offer_code_id"]
	feedback = request.POST["feedback"]

	try:
		offer_code = OfferCode.objects.get(id=offer_code_id)
		offer_code.feedback = feedback
		offer_code.save()
		data["result"] = 1
		data["result_msg"] = "Successfully added feedback."
	except OfferCode.DoesNotExist:
		# invalid offer code id
		data["result"] = -1
		data["result_msg"] = "Offer ID is invalid or has not been specified in POST parameter."

	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def offer_rate(request):
	"""
		Provide rate regarding a used offer

		:param rating: 1 to 5
	"""
	data = {}

	offer_code_id = request.POST["offer_code_id"]
	rating = request.POST["rating"]

	try:
		offer_code = OfferCode.objects.get(id=offer_code_id)
		offer_code.rating = rating 
		offer_code.save()
		data["result"] = 1
		data["result_msg"] = "Successfully rated."
	except OfferCode.DoesNotExist:
		# invalid offer code id
		data["result"] = -1
		data["result_msg"] = "Offer ID is invalid or has not been specified in POST parameter."

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
	phone = parse_phone_number(request.POST['phone'])
	zipcode = request.POST['zipcode']
	
	# need to clean up phone

	if not ZipCode.objects.filter(code=zipcode).exists():
		# ERROR: zip code is invalid
		data["result"] = -2
		data["result_msg"] = "Zip code is invalid or not yet registered in system."
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
		message = _("Here's your temporary password: %(password)s.	Please login to http://shoppley.com and update your password and you will be given free points to start sending Shoppley offers.") %{ "password": rand_passwd }
		recipients = [email]
		send_mail("Welcome to Shoppley", message, settings.DEFAULT_FROM_EMAIL, recipients)  
		txt_msg = _("%(password)s is temporary password from Shoppley") % { "password": rand_passwd }
		sms_notify(phone, txt_msg, SMS_DEBUG)
	else:
		# ERROR: User exists, ask user to login with their password 
		data["result"] = -1
		data["result_msg"] = "User already exists so you should login with their password."
		return JSONHttpResponse(data)	

	# you can start viewing offers	
	user = authenticate(username=email, password=rand_passwd)
	if user is not None:
		login(request, user)
		#logger.debug( "User %s authenticated and logged in"%email )
		data["result"] = 1
		data["result_msg"] = "User registered and authenticated successfully."
		return JSONHttpResponse(data)	 
	else:
		# ERROR: problem authenticating user
		data["result"] = -3
		data["result_msg"] = "Authentication error, possibly the user is not activated."
		return JSONHttpResponse(data)

@csrf_exempt
@login_required
def splash_view(request):
	"""
		Returns a summary of visitors 
			- this week (this week from Monday)
			- last week (last week)
			- past month (last 30 days window)
	"""

	data = {}

	u = request.user
	merchant = u.shoppleyuser.merchant

	now = datetime.now()
	today = datetime.now().weekday()
	monday = datetime.now()-timedelta(days=today)
	start_date = datetime(monday.year, monday.month, monday.day, 0, 0, 0) 
	end_date = datetime.now()
	data["this_week"] = OfferCode.objects.filter(offer__merchant=merchant, redeem_time__range=(start_date, end_date)).count()

	today = datetime.now().weekday()
	monday = datetime.now()-timedelta(days=today+8)
	sunday = datetime.now()-timedelta(days=today+1)
	start_date = datetime(monday.year, monday.month, monday.day, 0, 0, 0)
	end_date = datetime(sunday.year, sunday.month, sunday.day, 23, 59, 59)
	data["last_week"] = OfferCode.objects.filter(offer__merchant=merchant, redeem_time__range=(start_date, end_date)).count()

	start_date = datetime.now()-timedelta(days=30)
	end_date = datetime.now()
	data["past_month"] = OfferCode.objects.filter(offer__merchant=merchant, redeem_time__range=(start_date, end_date)).count()

	data["result"] = 1
	data["result_msg"] = "Number of redemptions for this week, last week and past month returned."
	
	return JSONHttpResponse(data)	
	
@csrf_exempt
@login_required
def offers_active(request):
	"""
		Returns currently active offers and their details
	"""
	data = {}

	u = request.user
	if u.shoppleyuser.is_merchant():
		merchant = u.shoppleyuser.merchant

		data["offers"] = []
		for o in Offer.objects.filter(merchant=merchant, expired=False):
			data["offers"].append( o.offer_detail() )

		data["result"] = 1
		data["result_msg"] = "Returned details of merchants currently active offers."
	else:
		data["result"] = -1
		data["result_msg"] = "Not a valid merchant user."
	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def offer_start(request):
	"""
		Offer parameters are defined and offer is started

		'title':'$10 off on entree',
		'description': 'Come taste some great greek food next 30 minutes',
		'now': False,
		'date': '2011-05-18',
		'time': '06:00:00 PM',
		'duration': 30,
		'units': 1,
		'amount': 10 

	"""

	data = {}

	# check if the necessary parameters are provided
	title = request.POST.get('title', None)
	description = request.POST.get('description', None)
	duration = int(request.POST.get('duration', 90))
	amount = int(request.POST.get('amount', 0))
	unit = int(request.POST.get('unit', 0))

	if title is None:
		title = description[:128]
	now = request.POST.get('now', False)
	if now:
		start_time = datetime.now()
	else:
		date = request.POST.get('date', None)
		time = request.POST.get('time', None)
		if time == None:
			start_time = datetime.now()
		elif date == None:
			today = datetime.now()
			start_time = datetime.strptime("%s-%s-%s %s"%(today.year, today.month, today.day, time), "%Y-%m-%d %I:%M:%S %p")
		else:
			# start at specified date and time
			start_time = datetime.strptime("%s %s"%(date, time), "%Y-%m-%d %I:%M:%S %p")

	u = request.user
	if u.shoppleyuser.is_merchant():
		merchant = u.shoppleyuser.merchant

		if unit == 0:
			# percent 
			offer = Offer(merchant=merchant, title=title,
					description=description, percentage=amount,
					duration=duration,
					time_stamp=datetime.now(),
					starting_time=start_time)
		else:
			# dollar
			offer = Offer(merchant=merchant, title=title,
					description=description, dollar_off=amount,
					duration=duration,
					time_stamp=datetime.now(),
					starting_time=start_time)
		offer.save()

		num_reached = offer.distribute()
		receipt_msg = _("Offers were sent but not clear how many people reached.")
		if num_reached ==0 :
			receipt_msg = _("There were no customers that could be reached at this moment.") 
		elif num_reached == -2:
			receipt_msg = _("Your balance is %d. You do not have enough to reach customers.") % merchant.balance

		data["offer"] = offer.offer_detail()
		data["result"] = num_reached 
		data["result_msg"] = receipt_msg 
	else:
		data["result"] = -1
		data["result_msg"] = "Not a valid merchant user."

	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def offer_send_more(request, offer_id):
	"""
		Offer is requested to be sent to more people
	"""
	data = {}

	u = request.user

	# check parameters 
	if offer_id is None:
		data["result"] = -2
		data["result_msg"] = "Parameter offer_id has not been specified."
		return JSONHttpResponse(data)

	if u.shoppleyuser.is_merchant():

		merchant = u.shoppleyuser.merchant

		try:
			offer = Offer.objects.get(merchant=merchant, id=offer_id)
			num_reached = offer.redistribute()

			receipt_msg = _("Offers were sent but not clear how many people reached.")
			if num_reached ==0 :
				receipt_msg = _("There were no customers that could be reached at this moment.") 
			elif num_reached == -2:
				receipt_msg = _("Your balance is %d. You do not have enough to reach customers.") % merchant.balance

			data["offer"] = offer.offer_detail()
			data["result"] = num_reached 
			data["result_msg"] = receipt_msg 

		except Offer.DoesNotExist:
			data["result"] = -3
			data["result_msg"] = "Parameter offer_id specified is not a valid offer."

	else:
		data["result"] = -1
		data["result_msg"] = "Not a valid merchant user."

	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def offer_restart(request, offer_id):
	"""
		Send the old offer information so it can be prefilled to create a new offer
	"""

	data = {}

	# check parameters 
	if offer_id is None:
		data["result"] = -2
		data["result_msg"] = "Parameter offer_id has not been specified."
		return JSONHttpResponse(data)

	u = request.user
	if u.shoppleyuser.is_merchant():
		merchant = u.shoppleyuser.merchant

		try:
			offer = Offer.objects.get(merchant=merchant, id=offer_id)
			data["offer"] = offer.offer_detail()
			data["result"] = 1
			data["result_msg"] = "Found the previous offer that will be prefilled the new offer." 
		except Offer.DoesNotExist:
			data["result"] = -3
			data["result_msg"] = "Parameter offer_id specified is not a valid offer."

	else:
		data["result"] = -1
		data["result_msg"] = "Not a valid merchant user."

	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def offer_redeem(request):
	data = {}

	# check parameters
	code = request.POST.get('code', None)
	amount = float(request.POST.get('amount', None))

	u = request.user
	if u.shoppleyuser.is_merchant():
		merchant = u.shoppleyuser.merchant

		try:
			offer = OfferCode.objects.get(offer__merchant=merchant, code = code)
			offer.redeem_time = datetime.now()
			offer.txn_amount = amount
			offer.save()

			data["offer_code"] = offer.offer_detail() 
			data["result"] = 1
			data["result_msg"] = "Offer redemption (code: %s) successful."%code
		except OfferCode.DoesNotExist:
			data["result"] = -2
			data["result_msg"] = "Offer code %s is not a valid code for your store."%code
	else:
		data["result"] = -1
		data["result_msg"] = "Not a valid merchant user."

	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def offers_past(request, days=0):
	"""
		Offers from past days
	"""
	data = {}

	days = int(days)
	u = request.user
	if u.shoppleyuser.is_merchant():
		merchant = u.shoppleyuser.merchant
		data["offers"] = []
		if days == 0:
			for o in Offer.objects.filter(merchant=merchant, expired=True):
				data["offers"].append( o.offer_detail() )
		else:
			start_date = datetime.now()-timedelta(days=days)
			end_date = datetime.now()
			for o in Offer.objects.filter(merchant=merchant, expired=True, starting_time__range=(start_date, end_date)):
				data["offers"].append( o.offer_detail() )

		data["result"] = 1
		data["result_msg"] = "Returned details of past offers."
	else:
		data["result"] = -1
		data["result_msg"] = "Not a valid merchant user."

	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def merchant_summary(request, days=7):
	"""
		Shows the 
		Number of offers sent out past week
		Number of offers reached
		Number of offers redeemed (percentage)
	"""

	data = {}

	u = request.user
	if u.shoppleyuser.is_merchant():
		merchant = u.shoppleyuser.merchant

		start_date = datetime.now()-timedelta(days=days)
		end_date = datetime.now()
		all_offers = Offer.objects.filter(merchant=merchant, starting_time__range=(start_date, end_date))
		data["num_offers"] = all_offers.count()
		direct_recvd = 0
		total_recvd = 0
		total_redeemed = 0
		for o in all_offers:
			direct_recvd += o.num_direct_received()
			total_recvd += o.num_received()
			total_redeemed += o.num_redeemed()	

		data["direct_received"] = direct_recvd
		data["total_received"] = total_recvd
		data["total_redeemed"] = total_redeemed
		if direct_recvd == 0:
			data["redeem_rate"] = 0
		else:
			data["redeem_rate"] = total_redeemed/float(direct_recvd)*100
			
		data["result"] = 1
		data["result_msg"] = "Summary data about the merchant's offers."
	else:
		data["result"] = -1
		data["result_msg"] = "Not a valid merchant user."

	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def merchant_summary_viz(request):
	data = {}

	u = request.user
	if u.shoppleyuser.is_merchant():
		merchant = u.shoppleyuser.merchant
		data["offer_id"] = 2

	else:
		data["result"] = -1
		data["result_msg"] = "Not a valid merchant user."

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

	u = request.user
	if u.shoppleyuser.is_merchant():
		merchant = u.shoppleyuser.merchant
		data["offer_id"] = 2

	else:
		data["result"] = -1
		data["result_msg"] = "Not a valid merchant user."


	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def point_offers_past(request):
	data = {}

	u = request.user
	if u.shoppleyuser.is_merchant():
		merchant = u.shoppleyuser.merchant
		data["offer_id"] = 2

	else:
		data["result"] = -1
		data["result_msg"] = "Not a valid merchant user."




	return JSONHttpResponse(data)	


@csrf_exempt
@login_required
def point_offer_start(request):
	data = {}

	u = request.user
	if u.shoppleyuser.is_merchant():
		merchant = u.shoppleyuser.merchant
		data["offer_id"] = 2

	else:
		data["result"] = -1
		data["result_msg"] = "Not a valid merchant user."


	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def point_offer_restart(request):
	data = {}

	u = request.user
	if u.shoppleyuser.is_merchant():
		merchant = u.shoppleyuser.merchant
		data["offer_id"] = 2

	else:
		data["result"] = -1
		data["result_msg"] = "Not a valid merchant user."

	return JSONHttpResponse(data)	

@csrf_exempt
@login_required
def point_offer_expire(request, offer_id):
	data = {}

	u = request.user
	if u.shoppleyuser.is_merchant():
		merchant = u.shoppleyuser.merchant
		data["offer_id"] = 2

	else:
		data["result"] = -1
		data["result_msg"] = "Not a valid merchant user."

	return JSONHttpResponse(data)	


