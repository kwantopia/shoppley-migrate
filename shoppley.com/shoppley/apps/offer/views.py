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

from django.utils.translation import ugettext as _
from django.utils.translation import ungettext, string_concat
from django.core.exceptions import MultipleObjectsReturned

from random import randint
from shoppleyuser.models import Customer 

if "mailer" in settings.INSTALLED_APPS:
    from mailer import send_mail
else:
    from django.core.mail import send_mail

# Python libraries
import os
import logging
from datetime import datetime, timedelta
from offer.forms import StartOfferForm
from buxfer.forms import BuxferLoginForm
from offer.models import *
from common.helpers import JSONHttpResponse


def index(request):
	data = {}

	return render_to_response("offer/homepage.html", data, context_instance=RequestContext(request))

@login_required
def offer_home(request):
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

			offer.name = self.cleaned_data.get("name")
			offer.description = self.cleaned_data.get("description")
			if len(offer.name) == 0:
				offer.name = description[:64] 

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

