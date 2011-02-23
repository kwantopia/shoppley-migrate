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

if "mailer" in settings.INSTALLED_APPS:
    from mailer import send_mail
else:
    from django.core.mail import send_mail

# Python libraries
import os
import logging
from datetime import datetime
from datetime import timedelta
import simplejson
from offer.forms import StartOfferForm

@login_required
def offer_home(request):
	return HttpResponse("This is the hoome")

def offer_send():
	print "Sending out offers"

@login_required
def start_offer(request):

	data = {}

	if request.method == "POST":
		form = StartOfferForm(request.POST)
		if form.is_valid():
			form.save()	
			# send out the offer
			offer_send()			
			data["result"] = "1"
			
			return JSONHttpResponse(data)
	else:
		form = StartOfferForm()

	data["form"] = form 
	return render_to_response("offer/start_offer.html", data,
						context_instance=RequestContext(request))

