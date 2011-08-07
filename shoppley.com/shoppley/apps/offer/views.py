# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context, loader
from django.core.urlresolvers import reverse
from django.core.files import File
from django.contrib.auth.models import User
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib import messages

from django.utils.translation import ugettext as _
from django.utils.translation import ungettext, string_concat
from django.core.exceptions import MultipleObjectsReturned

from random import randint
from shoppleyuser.models import Customer , Merchant, CustomerPhone, MerchantPhone

if "mailer" in settings.INSTALLED_APPS:
    from mailer import send_mail
else:
    from django.core.mail import send_mail

# Python libraries
import os
import logging

from datetime import datetime, date, time, timedelta
from offer.forms import StartOfferForm
from offer.models import Offer, OfferCode
from buxfer.forms import BuxferLoginForm

from offer.models import *
from common.helpers import JSONHttpResponse
from django.db.models import Sum

def index(request):
	data = {}

	return render_to_response("offer/homepage.html", data, context_instance=RequestContext(request))


@login_required
def offer_home(request):
	u = request.user
	if u.shoppleyuser:
		if u.shoppleyuser.is_merchant():
			return HttpResponseRedirect(reverse("offer.views.merchant_offer_home"))
		else:
			return HttpResponseRedirect(reverse("offer.views.customer_offer_home"))
	return HttpResponseRedirect(reverse("home"))

@login_required
def customer_offer_home(request, days = "7"):
	u = request.user
	try:
		customer = u.shoppleyuser.customer
		data = {}
		all_active_offers = Offer.objects.filter(expired_time__gt=datetime.now())
		all_exp_offers = Offer.objects.filter(expired_time__lt=datetime.now())

		rcv_offercodes = customer.offercode_set.order_by("-redeem_time")
		rcv_active_offercodes = customer.offercode_set.filter(expiration_time__gt=datetime.now()).order_by("-redeem_time")
		other_active_offers = all_active_offers.exclude(pk__in =customer.offercode_set.all())
		used_offercodes = customer.offercode_set.order_by("-redeem_time").filter(redeem_time__isnull=False)
		exp_rcv_offercodes = customer.offercode_set.filter(expiration_time__lt=datetime.now()).order_by("-expiration_time")
		return render_to_response("offer/customer_offer_home.html", 
						{
							"used_offercodes": used_offercodes,
							"rcv_offercodes": rcv_offercodes,
							"other_active_offers": other_active_offers,
							"total_points": customer.balance,
							"daily_limits": customer.daily_limit,
							"num_used_offercodes": used_offercodes.count(),
							"num_rcv_offercodes": rcv_offercodes.count() ,
							"num_exp_rcv_offercodes": exp_rcv_offercodes.count(),
							
						},
                                                context_instance=RequestContext(request))
	#except ShoppleyUser.DoesNotExist:
	#	return HttpResponseRedirect(reverse("shoppleyuser.views.home"))
	except Customer.DoesNotExist:
		return HttpResponseRedirect(reverse("offer.views.offer_home"))

@login_required
def merchant_offer_home(request, days= "7"):
	u = request.user
	merchant = u.shoppleyuser.merchant

	try:
		total_stats = [(i.num_init_sentto, i.offercode_set.filter(forwarder__isnull=False).count(), i.offercode_set.filter(redeem_time__isnull=False).count()) for i in merchant.offers_published.all()]
	#unique_customers
		d = date.today()
		
		days_ago = d + timedelta(days=-1*int(days))

		offercodes = OfferCode.objects.filter(Q(offer__merchant = merchant), Q(offer__time_stamp__gt=days_ago))
		unique_customers = offercodes.values("customer").distinct()
		total_forwards =offercodes.filter(forwarder__isnull=False).count()
		total_redeemed = offercodes.filter(redeem_time__isnull=False).count()
		total_sent = merchant.offers_published.aggregate(Sum('num_init_sentto'))
		past_offers = merchant.offers_published.filter(expired_time__lt=datetime.now())
		current_offers = merchant.offers_published.filter(expired_time__gt=datetime.now())
		scheduled_offers = merchant.offers_published.filter(time_stamp__gt=datetime.now())

		return render_to_response("offer/merchant_offer_home.html",
					{
						"all_offers": merchant.offers_published.all(),
						"past_offers": past_offers,
						"current_offers": current_offers,
						"scheduled_offers": scheduled_offers,
						"total_forwards": total_forwards,
						"total_redeemed": total_redeemed,
						"total_sent": total_sent,
						"balance": merchant.balance,
						"biz_name": merchant.business_name,
						},
                                                context_instance=RequestContext(request))
	except Merchant.DoesNotExist:
		return HttpResponseRedirect(reverse("offer.views.offer_home"))

@login_required
def merchant_start_offer(request):
	pass

@login_required
def merchant_track_offer(request):
	pass

@login_required
def offer_home_1(request):
	"""
		Allow customer to view list of received offers
	"""
	data = {}

	u = request.user

	if u.shoppleyuser.is_merchant():
		return HttpResponseRedirect(reverse("offer.views.start_offer"))

	data["offers_received"] = OfferCode.objects.filter(customer=u.shoppleyuser.customer, redeem_time__isnull=True)	
	data["offers_redeemed"] = OfferCode.objects.filter(customer=u.shoppleyuser.customer, redeem_time__isnull=False)	

	# top 5 featured places
	data["featured"] = Feature.objects.all().order_by("time_stamp")[:5]
	data["buxfer_form"] = BuxferLoginForm()

	return render_to_response("offer/customer_home.html", data,
					context_instance=RequestContext(request))

@login_required
def start_offer(request):

	data = {}
	
	u = request.user

	if u.shoppleyuser.is_customer():
		return HttpResponseRedirect( reverse("offer.views.offer_home") )

	if request.method == "POST":
		form = StartOfferForm(request.POST)
		if form.is_valid():
			offer = form.save(commit=False)	
			offer.merchant = u.shoppleyuser.merchant
			offer.time_stamp = datetime.now()

			if form.cleaned_data["now"]:
				offer.starting_time = datetime.now()+timedelta(minutes=5)

			offer.title = self.cleaned_data.get("title")
			offer.description = self.cleaned_data.get("description")
			if len(offer.title) == 0:
				offer.title = description[:64] 

			if form.cleaned_data.get("offer_radio") == 0:
				offer.percentage = self.cleaned_data.get("percentage")	
				offer.dollar_off = None
			elif form.cleaned_data.get("offer_radio") == 1:
				offer.dollar_off = self.cleaned_data.get("dollar_off")	
				offer.percentage = None

			offer.save()
			# send out the offer
			num_sent = offer.distribute()			
			data["result"] = "1"
			data["offer"] = offer
			data["num_sent"] = num_sent
			# past and current offers
			# TODO: would be more efficient if there was a way to filter active and past offers separately instead of doing it on template
			data["offers"] = Offer.objects.filter(merchant=u.shoppleyuser.merchant).order_by("-time_stamp")
			data["form"] = StartOfferForm()
			
			return render_to_response("offer/start_offer.html", data,
						context_instance=RequestContext(request))
		else:
			data["result"] = "-1"
	else:
		data["offers"] = Offer.objects.filter(merchant=u.shoppleyuser.merchant).order_by("-time_stamp")
		form = StartOfferForm(initial={'offer_radio':0})

	data["form"] = form 
	return render_to_response("offer/start_offer.html", data,
						context_instance=RequestContext(request))


from django.core import serializers

#@login_required
def test_offer(request):

	data = {}
	
	#u = request.user
	u = User.objects.get(email="kool@mit.edu")

	if u.shoppleyuser.is_customer():
		return HttpResponseRedirect( reverse("offer.views.offer_home") )

	if request.method == "POST":
		form = StartOfferForm(request.POST)
		if form.is_valid():
			offer = form.save(commit=False)	
			offer.merchant = u.shoppleyuser.merchant
			offer.time_stamp = datetime.now()
			if form.cleaned_data["now"]:
				offer.starting_time = datetime.now()+timedelta(minutes=5)
			offer.save()
			# send out the offer
			num_sent = offer.distribute()			
			data["result"] = "1"
			data["offer_id"] = offer.id
			data["num_sent"] = num_sent
			return JSONHttpResponse(data)	
		else:
			data["result"] = "-1"
	else:
		data["result"] = "-2"
		form = StartOfferForm()

	data["form"] = str(form)

	return JSONHttpResponse(data)

