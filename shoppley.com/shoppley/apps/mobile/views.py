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

from common.helpers import JSONHttpResponse, JSHttpResponse

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
#@login_required
def mobile_logout(request):
	data = {}
	logout(request)
	data["result"] = 1 
	return JSONHttpResponse(data)	

@csrf_exempt
def register_customer(request):
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
##@login_required
def offers_current(request):
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
#@login_required
def offers_redeemed(request):
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
#@login_required
def offer_forward(request):
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
#@login_required
def offer_feedback(request):
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
#@login_required
def offer_rate(request):
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
#@login_required
def offer_rate(request):
	data = {}
	return JSONHttpResponse(data)	


#####################################
# Merchant mobile API
#####################################

@csrf_exempt
def register_merchant(request):
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
#@login_required
def splash_view(request):
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
#@login_required
def offers_active(request):
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
#@login_required
def offer_start(request):
	data = {}
	data["offer_id"] = 1
	return JSONHttpResponse(data)	

@csrf_exempt
#@login_required
def offer_send_more(request, offer_id):
	data = {}
	data["offer_id"] = 2
	return JSONHttpResponse(data)	

@csrf_exempt
#@login_required
def offer_restart(request):
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
#@login_required
def offer_redeem(request):
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
#@login_required
def offers_past(request):
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
#@login_required
def merchant_summary(request):
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
#@login_required
def merchant_summary_viz(request):
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
#@login_required
def offers_all(request):
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
#@login_required
def point_summary(request):
	"""
		for the customer
	"""
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
#@login_required
def point_offers(request):
	"""
		for the customer
	"""
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
#@login_required
def point_offer(request, offer_id):
	"""
		for the customer, details of a point offer
	"""
	data = {}
	return JSONHttpResponse(data)	

@csrf_exempt
#@login_required
def point_offer_start(request):
	data = {}
	data["offer_id"] = 1
	return JSONHttpResponse(data)	

@csrf_exempt
#@login_required
def point_offer_expire(request, offer_id):
	data = {}
	return JSONHttpResponse(data)	


