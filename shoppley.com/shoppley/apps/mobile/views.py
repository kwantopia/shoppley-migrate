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
from common.customer import customer_authenticate, customer_register, customer_iwant, customer_get_current_forward_offers
from shoppleyuser.utils import sms_notify, parse_phone_number, pretty_date
from shoppleyuser.models import ZipCode, Merchant, Customer, ShoppleyPhone, MerchantPhone, CustomerPhone
from offer.models import Offer, OfferCode

# for generating random password
import random, string, time
from datetime import datetime, timedelta

SMS_DEBUG = True

@csrf_exempt
def mobile_login(request):
	email = request.POST['email'].lower()
	password = request.POST['password']
	data = customer_authenticate(request, email, password)
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
	email = request.POST['email'].lower()
	phone = parse_phone_number(request.POST['phone'])
	zipcode = request.POST['zipcode']
	password = request.POST['password']
    
	#TODO check null
	data = customer_register(email, None, zipcode, phone, password, None, None)
	
	if data["result"] == 1:
		data = customer_authenticate(request, data["username"], data["password"]);
		
	return JSONHttpResponse(data)
			
@csrf_exempt
@login_required
def offers_current(request):
	"""

		:param lat: current latitude (can be "")
		:param lon: current longitude (can be "")

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
		customer = u.shoppleyuser.customer
		
		lat = request.POST.get("lat", None)
		lon = request.POST.get("lon", None)
			
		if (lat is not None) and (lon is not None):
			if (lat != "") and (lon != ""):
				customer.set_location_from_latlon(lat, lon)
		
		v = request.POST.get("v", 0)
		if v == 0:
			user_offers = OfferCode.objects.filter(customer=customer, expiration_time__gt=datetime.now())
			#print "******** checking offers ************"
			#print user_offers.count()
			data["num_offers"] = user_offers.count()
			data["offers"] = []

			#"expiration": str(time.mktime(o.expiration_time.timetuple())),
			for o in user_offers:
				data["offers"].append(o.offer_detail())	
			data["result"] = 1
			data["result_msg"] = "Returning offer details."
		else:
			data["forward_offers"] = []
			forward_offers = customer_get_current_forward_offers(customer)
			forward_offers_ids = []
			
			for o in forward_offers:
				if o.offer.id not in forward_offers_ids:
					data["forward_offers"].append(o.offer_detail())
					forward_offers_ids.append(o.offer.id)

			# (yod) 5 is magic number
			data["offers"] = []
			user_offers = customer.get_offers_within_miles(5)
			for o in user_offers:
				if o.id not in forward_offers_ids:
					data["offers"].append(o.customer_offer_detail(customer))
				
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
	data["result"] = -999
	data["result_msg"] = "Don't call me."
	return JSONHttpResponse(data)

@csrf_exempt
@login_required
def offer_get_offercode(request):
	"""
		:param offer_id: offer id to generate code for
	"""
	data = {}
	
	offer_id = request.POST.get("offer_id", None)
	if offer_id is None:
		data["result"] = -2
		data["result_msg"] = "offer_id is required."
		return JSONHttpResponse(data)

	u = request.user
	if u.shoppleyuser.is_customer():
		customer = u.shoppleyuser.customer
		
		try:
			o = Offer.objects.get(id=offer_id)
			o.gen_offer_code(customer)
			
			data["offer"] = o.customer_offer_detail(customer)
			data["result"] = 1
			data["result_msg"] = "^_^"
			
		except Offer.DoesNotExist:
			data["result"] = -3
			data["result_msg"] = "Offer does not exists."
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
		:param emails: list of emails 
		:param note: a note for the friend

	"""
	data = {}

	u = request.user
	customer = u.shoppleyuser.customer

	offer_code = request.POST.get("offer_code", None)
	phones = request.POST.getlist("phones")
	emails = request.POST.getlist("emails")
	notes = request.POST.get("note", "")

	if offer_code and len(phones) > 0:
		if OfferCode.objects.filter(code__iexact=offer_code).exists():
			original_code = OfferCode.objects.filter(code__iexact=offer_code)[0]
			offer = original_code.offer
			for phone in phones:
				new_code, random_pw = offer.gen_forward_offercode(original_code, phone)
				# text the user the user name and password

				customer_msg = _("%(customer)s forwarded you an offer!\n*from: %(merchant)s\n*title: %(description)s\n*expires: %(expiration)s\nCome redeem w/ [%(code)s]\n")%{
						"customer": customer.phone,
						"merchant": offer.merchant,
						"expiration": pretty_date(original_code.expiration_time),
						"description": offer.description,
						"dollar_off": offer.dollar_off,
						"code": new_code.code,
						}
				#TODO: if the person do not mind receiving txt
				sms_notify(phone,customer_msg, SMS_DEBUG)

				if random_pw:
					new_customer = new_code.customer
					#print "created a customer for %s" % friend_num
					account_msg = _("Welcome to Shoppley! shoppley.com login info:\n-username: %(name)s\n-password: %(password)s\nTxt #help to %(shoppley)s to get started.")%{"name":new_customer.user.username,"password":random_pw, "shoppley": settings.SHOPPLEY_NUM}
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

@csrf_exempt
@login_required
def iwant(request):
	data = {}
	
	request_text = request.POST.get("request", None)
	if request_text is None:
		data["result"] = -1
		data["result_msg"] = "missing key: 'request'"
		return JSONHttpResponse(data)
	
	u = request.user
	customer = u.shoppleyuser.customer
	customer_iwant(customer, request_text)

	data["result"] = 1
	data["result_msg"] = "Success"
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
		MerchantPhone.objects.create(number=phone, merchant=c)

		# send a text message and e-mail with random password
		message = _("Here's your temporary password: %(password)s.	Please login to http://shoppley.com and update your password and you will be given free points to start sending Shoppley offers.") %{ "password": rand_passwd }
		recipients = [email]
		send_mail("Welcome to Shoppley", message, settings.DEFAULT_FROM_EMAIL, recipients)  
		txt_msg = _("%(password)s is temporary password for shoppley.com. Txt #help to %(shoppley)s to get started.") % { "password": rand_passwd, "shoppley":settings.SHOPPLEY_NUM }
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
	
@never_cache
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
		#active_offers = [o for o in Offer.objects.filter(merchant=merchant, expired_time__gt=datetime.now())].order_by('-starting_time')
		for o in Offer.objects.filter(merchant=merchant, expired_time__gt=datetime.now()).order_by('-starting_time'):
		
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
		'amount': 10,
		'lat': 42.32342,
		'lon': -23.2342
		
		(optional) 'start_unixtime' instead of date & time

	"""

	data = {}

	# check if the necessary parameters are provided
	title = request.POST.get('title', None)
	description = request.POST.get('description', None)
	duration = int(request.POST.get('duration', 90))
	amount = int(request.POST.get('amount', 0))
	unit = int(request.POST.get('units', 0))
	lat = float(request.POST.get('lat', 0))
	lon = float(request.POST.get('lon', 0))
	
	if (title is None or title == "") and (description is None or description == ""):
	    data["result"] = -1
	    data["result_msg"] = "Please provide title and description."
	    return JSONHttpResponse(data)

	if title is None:
		title = description[:128]
	now = request.POST.get('now', False)
	start_unixtime = request.POST.get('start_unixtime', None)
	if now:
		start_time = datetime.now()
	elif start_unixtime is not None:
		start_time = datetime.fromtimestamp(float(start_unixtime))
	else:
		date = request.POST.get('date', None)
		time = request.POST.get('time', None)
		if (time is None) or (date is None):
			data["result"] = -1
			data["result_msg"] = "Please provide start date & time."
			return JSONHttpResponse(data)

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
		offer.expired_time = offer.starting_time + timedelta(minutes=offer.duration)
		offer.save()

        # save location where the offer was generated to track merchant location
		if (lat is not 0) and (lon is not 0):
			offer.set_location_from_latlon(lat,lon)

		num_reached = 0
		receipt_msg = _("Offer has been submitted.  We are actively looking for customers.  Check back in a few minutes for status update.")
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
		data["result_msg"] = _("Parameter offer_id has not been specified.")
		return JSONHttpResponse(data)

	if u.shoppleyuser.is_merchant():

		merchant = u.shoppleyuser.merchant

		try:
			offer = Offer.objects.get(merchant=merchant, id=offer_id)
			if offer.redistribute():
				num_reached = 0 
				receipt_msg = _("Offer has been submitted.  We are actively looking for customers.  Check back in a few minutes for status update.")
			else:
				num_reached = -5
				receipt_msg = _("Offer has already been redistributed so you cannot resend.")

			data["offer"] = offer.offer_detail()
			data["result"] = num_reached 
			data["result_msg"] = receipt_msg 

		except Offer.DoesNotExist:
			data["result"] = -3
			data["result_msg"] = _("Parameter offer_id specified is not a valid offer.")

	else:
		data["result"] = -1
		data["result_msg"] = _("Not a valid merchant user.")

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
			
			for o in Offer.objects.filter(merchant=merchant, expired_time__lt=datetime.now()).order_by('-starting_time'):
			
				data["offers"].append( o.offer_detail(past=True) )
		else:
			start_date = datetime.now()-timedelta(days=days)
			end_date = datetime.now()
			#offers = [ o for o in Offer.objects.filter(merchant=merchant, starting_time__range=(start_date,end_date)) if o.is_active()==False]
			for o in Offer.objects.filter(merchant=merchant, expired_time__lt=datetime.now(), starting_time__range=(start_date, end_date)):
			
				data["offers"].append( o.offer_detail(past=True) )

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

		data["total_received"] = total_recvd
		data["total_forwarded"] = total_recvd - direct_recvd
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


