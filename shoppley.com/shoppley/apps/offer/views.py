# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context, loader
from django.core.urlresolvers import reverse
from django.core.files import File
from django.contrib.auth.models import User
from django.db.models import Q, Avg
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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

from datetime import datetime, date, time,timedelta
from offer.forms import StartOfferForm,AdminStartOfferForm, MerchantSearchForm
from offer.models import Offer, OfferCode
from offer.utils import get_days_ago, TxtTemplates
from buxfer.forms import BuxferLoginForm

from offer.models import *
from common.helpers import JSONHttpResponse
from django.db.models import Sum



def index(request):
	data = {}

	return render_to_response("offer/homepage.html", data, context_instance=RequestContext(request))


def merchant_offer(request, offer_id):
	pass

def customer_offer(request, offer_id):
	try:

		offer = Offer.objects.get(id=int(offer_id))
		data = {}
		data["title"] = offer.title
		data["description"] =offer.description,
		data["expiration"] = pretty_date(offer.expired_time, True),
		data["quantity"] = offer.max_offers
		data["duration"] = offer.duration
		data["banner"] = offer.merchant.banner
		data["merchant"] = offer.merchant.business_name
		data["id"] = offer.id
		data["site"] = "http://" + Site.objects.get(id=3).domain
		data["lat"] = offer.merchant.location.location.y
		data["lon"] = offer.merchant.location.location.x
		data["url"] = offer.merchant.url
		data["yelp_url"] = offer.merchant.yelp_url
		data["fb_url"] = offer.merchant.fb_url
		data["twitter_url"]  = offer.merchant.twitter_url
		try:
			user = request.user
			if not user.is_anonymous():
				u = user.shoppleyuser
				customer = u.customer
				if customer.offercode_set.filter(offer = offer).exists():
					data["code"] = customer.offercode_set.filter(offer=offer)[0].code
		except Exception, e:
			pass
		return render_to_response("offer/customer_offer.html", data, context_instance=RequestContext(request))
	except Offer.DoesNotExist:
		return HttpResponseRedirect(reverse("home"))

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
		try:
			page = int(request.GET.get("page"))
		except Exception , e:
			page = 1
		customer = u.shoppleyuser.customer
		days_ago = get_days_ago(days)
		all_active_offers = Offer.objects.filter(expired_time__gt=datetime.now())
		all_exp_offers = Offer.objects.filter(expired_time__lt=datetime.now())

		rcv_offercodes = customer.offercode_set.order_by("-redeem_time")
		rcv_active_offercodes = customer.offercode_set.filter(expiration_time__gt=datetime.now()).order_by("-redeem_time")
		other_active_offers = all_active_offers.exclude(pk__in =customer.offercode_set.all())
		used_offercodes = customer.offercode_set.order_by("-redeem_time").filter(redeem_time__isnull=False)
		exp_rcv_offercodes = customer.offercode_set.filter(expiration_time__lt=datetime.now()).order_by("-expiration_time")

		paginator = Paginator(other_active_offers, 10)
		total_pages = paginator.num_pages

		try:
			offer_list= paginator.page(page)
		except PageNotAnInteger:
			offer_list = paginator.page(1)
		except EmptyPage:
			offer_list = paginator.page(total_pages)


		return render_to_response("offer/customer_offer_home.html", 
						{
							"used_offercodes": used_offercodes,
							"rcv_offercodes": rcv_offercodes,
							"other_active_offers": offer_list,
							"total_points": customer.balance,
							"daily_limits": customer.daily_limit,
							"num_used_offercodes": used_offercodes.count(),
							"num_rcv_offercodes": rcv_offercodes.count() ,
							"num_exp_rcv_offercodes": exp_rcv_offercodes.count(),
							"page": page,
							"total_pages": total_pages,
							
							
						},
                                                context_instance=RequestContext(request))
	#except ShoppleyUser.DoesNotExist:
	#	return HttpResponseRedirect(reverse("shoppleyuser.views.home"))
	except Customer.DoesNotExist:
		return HttpResponseRedirect(reverse("offer.views.offer_home"))

@login_required
def merchant_offer_home(request, days= "7"):
	u = request.user
	
	try:

		try:
			page = int(request.GET.get("page"))
		except Exception , e:
			page = 1

		merchant = u.shoppleyuser.merchant
		total_stats = [(i.num_init_sentto, i.offercode_set.filter(forwarder__isnull=False).count(), i.offercode_set.filter(redeem_time__isnull=False).count()) for i in merchant.offers_published.all()]

		days_ago = get_days_ago(days)	
		offercodes = OfferCode.objects.filter(Q(offer__merchant = merchant), Q(offer__time_stamp__gt=days_ago))
		unique_customers = offercodes.values("customer").distinct()
		total_forwards =offercodes.filter(forwarder__isnull=False).count()
		total_redeemed = offercodes.filter(redeem_time__isnull=False).count()
		total_sent = merchant.offers_published.aggregate(Sum('num_init_sentto'))
		past_offers = merchant.offers_published.filter(expired_time__lt=datetime.now())
		current_offers = merchant.offers_published.filter(expired_time__gt=datetime.now())
		scheduled_offers = merchant.offers_published.filter(time_stamp__gt=datetime.now())

		paginator = Paginator(past_offers, 10)
		total_pages = paginator.num_pages
		
		try:
			offer_list= paginator.page(page)
		except PageNotAnInteger:
			offer_list = paginator.page(1)
		except EmptyPage:
			offer_list = paginator.page(total_pages)

		return render_to_response("offer/merchant_offer_home.html",
					{
						"all_offers": merchant.offers_published.all(),
						"past_offers": offer_list,
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
def customer_offer_sendme(request, offer_id):
	u = request.user
	try:
		customer = u.shoppleyuser.customer
		offer = Offer.objects.get(id = offer_id)
		offer.gen_offer_code(customer, 4)
		code =offer.offercode_set.get(customer=customer).code
		return HttpResponse("1")
	except:
		return HttpResponse("0")


@login_required
def admin_start_offer(request, merchant_id="-1", template = "offer/admin_start_offer.html"):
	#verify:
	u = request.user
	print "entering admin_start"
	if not u.is_superuser:
		return  HttpResponseRedirect(reverse("offer.views.offer_home"))
	if request.method=='POST':
		form = AdminStartOfferForm(request.POST, request.FILES)
		merchant = Merchant.objects.get(id=merchant_id)
		if form.is_valid():
			merchant = Merchant.objects.get(id=form.cleaned_data["merchant_id"])
			offer_type = form.cleaned_data["offer_radio"]
			value = form.cleaned_data["value"]
			now = form.cleaned_data["now"]
			description = form.cleaned_data["description"]
			title = form.cleaned_data["title"]
			if now :
			        time_stamp = datetime.now()
			else:
			        time_stamp = self.cleaned_data["date"]
			max_offers = form.cleaned_data["max_offers"]
			duration = form.cleaned_data["duration"]
			expiration = datetime.now() + timedelta(duration)
			Offer(merchant = merchant, title = title, description = description, time_stamp = datetime.now(), starting_time = time_stamp, duration = duration , max_offers = max_offers, expired_time = expiration).save()
			print "offer successfully created"
			return render_to_response("offer/offer_confirmation.html", {"offer": title, "business_name": merchant.business_name, "expiration": expiration, "address": merchant.print_address() },context_instance=RequestContext(request))
	else:
		if merchant_id == "-1":
			return HttpResponseRedirect(reverse("home"))
		merchant = Merchant.objects.get(id=merchant_id)
		print "creating new admin form"
		form = AdminStartOfferForm(initial={'merchant_id': merchant_id,})
	return render_to_response(template,{"form": form,"id": merchant_id, "business_name": merchant.business_name, "address": merchant.print_address(),},
                                context_instance=RequestContext(request))

@login_required
def search_merchant(request, template="offer/search_merchant.html"):
	u = request.user
	if not u.is_superuser:
		return  HttpResponseRedirect(reverse("offer.views.offer_home"))
	if request.method=='POST':
		form = MerchantSearchForm(request.POST)
		if form.is_valid():
			business_name = form.cleaned_data["business_name"].split()
			business_number =parse_phone_number( form.cleaned_data["business_num"])
			m=None
			if business_number and MerchantPhone.objects.filter(number=business_number).exists():
				m = MerchantPhone.objects.get(number=business_number).merchant
			elif business_name and Merchant.objects.filter(business_name__icontains=business_name).exists():
				m = Merchant.objects.get(business_name=business_name)
			if not m:
				return HttpResponseRedirect(reverse("home"))
			print "creating offer for ", m
			#return HttpResponseRedirect(reverse("admin_start_offer",args=str(m.id)))
			return HttpResponseRedirect(reverse("admin_start_offer", kwargs={"merchant_id":str( m.id), }))
	else:

		form = MerchantSearchForm()
	return render_to_response(template, {"form":form,},  context_instance=RequestContext(request))

@login_required
def merchant_start_offer(request,template = "offer/merchant_offer_start.html"):
	if request.method == 'POST':
		form = StartOfferForm(request.POST, request.FILES)
		if form.is_valid():
			user = request.user
			merchant = user.shoppleyuser.merchant
			#offer_type = form.cleaned_data["offer_radio"]
			value = float(form.cleaned_data["value"])
			description = form.cleaned_data["description"]
			title = form.cleaned_data["title"]
			d =  form.cleaned_data["date"]
			t = form.cleaned_data["time"]
			time_stamp = datetime.combine(d,t)
			max_offers = form.cleaned_data["max_offers"]
			duration = form.cleaned_data["duration"]
			discount_obj = form.cleaned_data["discount"]
			discount_obj = discount_obj.split(':::')
			discount = float(discount_obj[0])
			discount_type = discount_obj[1]
			dollar_off = 0
			percentage = 0
			discount_str = "None"
			if discount_type == '%':
				dollar_off = discount * value
				percentage = int(discount)
			
			elif discount_type == '$':
				dollar_off = discount
				percentage = int(100.0*discount / value)
			if discount_type != 'custom':
				discount_str = ''.join(discount_obj)
			expiration = time_stamp + timedelta(minutes=duration)
			Offer(merchant = merchant, title = title, description = description, time_stamp = time_stamp, starting_time = time_stamp, duration = duration , max_offers = max_offers, expired_time =expiration , offer_value= value, dollar_off = dollar_off, percentage=percentage).save()
			#return HttpResponseRedirect(reverse("offer.views.offer_home"))
			t = TxtTemplates()
			templates = TxtTemplates.templates
			txt_preview =t.render(templates["CUSTOMER"]["INFO"],
                                        {
                                                "offercode": "xxxx",
                                                "description":title,
                                                "merchant": merchant,
                                                "expiration": expiration,
                                        })
			return render_to_response("offer/offer_confirmation.html", 
						{"offer": title, 
						"business_name": merchant.business_name, 
						"expiration": expiration, 
						"address": merchant.print_address(),
						 "value": value,
						"discount": discount_str,
						"starting_time": time_stamp,
						"max_offers": max_offers,
						"description" :description,
						"txt_preview": txt_preview,
						},context_instance=RequestContext(request))
	else:

		form = StartOfferForm(initial={"value": '0', 
						"date": datetime.today()})
	return render_to_response(template,{"form": form,}, 
				context_instance=RequestContext(request))

		


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

