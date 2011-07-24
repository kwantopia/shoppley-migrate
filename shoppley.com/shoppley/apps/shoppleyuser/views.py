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
#from django.utils.translation import ugettext as _
from django.utils.translation import ungettext, string_concat
from django.core.exceptions import MultipleObjectsReturned
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _, ugettext
from emailconfirmation.models import EmailAddress

if "mailer" in settings.INSTALLED_APPS:
	from mailer import send_mail
else:
	from django.core.mail import send_mail

# Python libraries
import os, logging, json, random
from datetime import datetime, timedelta
from common.helpers import JSONHttpResponse

from account.utils import get_default_redirect
from account.forms import LoginForm
from shoppleyuser.forms import MerchantSignupForm, CustomerSignupForm,CustomerBetaSubscribeForm, CustomerProfileEditForm , MerchantProfileEditForm,CustomerExtraInfoForm, MerchantExtraInfoForm
from shoppleyuser.models import Customer, ShoppleyUser, Merchant, ZipCode
from django.views.decorators.csrf import csrf_exempt
from socialregistration import signals
from socialregistration import models

SAMPLE_OFFERS = ["25% off your entree if you come in next 2 hours",
			  "FREE orange juice with late lunch",
			  "Buy one get second pair of pants 50% off"]


def fb_connect_init(request):
	user = request.user
	try:
		su = user.shoppleyuser
		return HttpResponseRedirect(reverse("fb_login"))
	except ShoppleyUser.DoesNotExist:


		fbuser = request.facebook.graph.get_object("me")
		if fbuser['email']:
			try:
				EmailAddress.objects.get(email=fbuser['email'])
				request.user.delete()
			
				return HttpResponseRedirect(reverse("home_fb_fail")) ## user already have an account with us with the email.
			except EmailAddress.DoesNotExist:
				pass
		return 	HttpResponseRedirect(reverse("fb_extra_info"))

def home_fb_fail (request):
	return  render_to_response("front-page.html",{"lform":LoginForm,"error":"1", },context_instance=RequestContext(request))

def fb_login (request):
	return HttpResponseRedirect(reverse("home"))


def fb_customer_extra_info(request, success_url =None):
	if request.method=="POST":
		form = CustomerExtraInfoForm(request.POST,request=request)
		if form.is_valid():
			form.save()

			return HttpResponseRedirect(reverse("fb_connect_success"))
	else:
		print "In view -", request.user
		form = CustomerExtraInfoForm(request= request)
	fbuser= request.facebook.graph.get_object("me")
	print fbuser['email'], fbuser['first_name'], fbuser['last_name']
	
	ctx = { "form": form, }
	
	return render_to_response("shoppleyuser/cfb_extra_info_html",ctx , context_instance=RequestContext(request))

def fb_merchant_extra_info(request, success_url =None):
        if request.method=="POST":
                form = MerchantExtraInfoForm(request.POST,request=request)
                if form.is_valid():
                        form.save()
                        return HttpResponseRedirect(reverse("fb_connect_success"))
        else:
		
                form = MerchantExtraInfoForm(request= request)
        ctx = { "form": form, }

        return render_to_response("shoppleyuser/mfb_extra_info_html",ctx , context_instance=RequestContext(request))

def fb_connect_success(request):
	friends = request.facebook.graph.get_connections("me", "friends")
	return HttpResponseRedirect(reverse("home"))

# view for home, depending on whether request user is cutomer/merchant
def home(request,  template_name="front-page.html"):
	#return HttpResponseRedirect("http://webuy-dev.mit.edu")
	user = request.user
	if user.is_authenticated():
		try:
			su= user.shoppleyuser
			if user.shoppleyuser.is_customer():
				if request.user.emailaddress_set.count()==0:

					messages.add_message(request, messages.INFO,
						'You do not have an email yet. Please go to <a href="/shoppleyuser/customer/profile-settings/">Account</a> and add one for email notifications')
				zipcode = user.shoppleyuser.customer.zipcode

				number = user.shoppleyuser.customer.count_merchants_within_miles()

				messages.add_message(request, messages.INFO, 'Currently,<span style="font-weight:bold"> %s</span> stores in your area have signed up with Shoppley. Tell your favorite stores to use Shoppley to send you any last minute offers for free.' % number)

			
				return render_to_response("shoppleyuser/customer_landing_page.html", 
									{"number":number,
									},
								context_instance=RequestContext(request))
			else:

				if not user.shoppleyuser.merchant.address_1:
					messages.add_message(request, messages.INFO,
                                                'We do not have your business address. Please go to <a href="/shoppleyuser/merchant/profile-settings/">Account</a> and add one.')
	
				zipcode = user.shoppleyuser.merchant.zipcode
				number = user.shoppleyuser.merchant.count_customers_within_miles()

				messages.add_message(request, messages.INFO, 'Currently,<span style="font-weight:bold"> %s</span> people in your area have signed up to receive offer. Tell your customers to sign up for Shoppley to receive last minute offers for free.' % number)

				ie_offer = random.sample(SAMPLE_OFFERS, 1)[0]

				return render_to_response("shoppleyuser/merchant_landing_page.html", 
									{"number":number,
									"ie_offer": ie_offer,
									},
							context_instance=RequestContext(request))
		except ShoppleyUser.DoesNotExist:
			print "No shoppleyuser"
			return  render_to_response(template_name,{
                                        "lform":LoginForm,
					"no_shoppleyuser_linked": "1",
                                },context_instance=RequestContext(request))
	else:

		return	render_to_response(template_name,{
					"lform":LoginForm,
				},context_instance=RequestContext(request))


def account_test (request, template_name = "account/account.html"):
	try:
		shoppleyuser = request.user.shoppleyuser
		##shoppleyuser =ShoppleyUser.objects.get(user__id=request.user.id)	
		return render_to_response(template_name,{
					"shoppleyuser":shoppleyuser,
			}, context_instance=RequestContext(request))
	except ShoppleyUser.DoesNotExist:
		pass

def account_info(request, template_name="shoppleyuser/account_info.html"):
	try:
		shoppleyuser = request.user.shoppleyuser
		#shoppleyuser =ShoppleyUser.objects.get(user__id=request.user.id)
		return render_to_response(template_name,{
					"shoppleyuser":shoppleyuser,
				}, context_instance=RequestContext(request))
	except ShoppleyUser.DoesNotExist:
		pass
		

def account_set_offer_limit(request, template_name="shoppleyuser/account_set_offer_limit.html"):
	if request.method== "POST":
		pass

def offer_frequency_set(request, template_name="shoppleyuser/offer_frequency_set.html"):
	try:
		customer = request.user.shoppleyuser.customer
		#customer = Customer.objects.get(user__id = request.user.id)
		return render_to_response(template_name,{
					"frequency":customer.frequency,
				}, context_instance=RequestContext(request))
	except Customer.DoesNotExist:
		pass

@login_required
@csrf_exempt
def set_user_timezone(request):
	#print "anything here"
	#return HttpResponse("1")
	if request.method=="POST":
		print "hello"
		timezone = request.POST["tz"]
		print "timezone" , timezone
		u= request.user.shoppleyuser
		if u:
			#u = request.user.shoppleyuser
			u.timezone = timezone
			u.save()
			return HttpResponse("1")
		else:
			return HttpResponse("0")

def login(request, form_class=LoginForm, template_name="account/login.html",
			success_url=None, associate_openid=False, openid_success_url=None,
			url_required=False, extra_context=None):
	if extra_context is None:
		extra_context = {}
	if success_url is None:
		success_url = get_default_redirect(request)
	if request.method == "POST" and not url_required:
		form = form_class(request.POST)
		#print ">>>>>>>>>>>> GET HERE FIRST??"
		if form.is_valid():


				## HACK For now. Dont know why form.login(request) returns false!!

				## TODO HACK For now. Dont know why form.login(request) returns false!!

			# if form.login(request):
				form.login(request)
				try:
					s = request.user.shoppleyuser
					#s = ShoppleyUser.objects.get(user__id=request.user.id)
					s.verified=True
					s.save()
				except ShoppleyUser.DoesNotExist:	
					# user wasnt registered yet.
					pass

				if associate_openid and association_model is not None:
					for openid in request.session.get('openids', []):
						assoc, created = UserOpenidAssociation.objects.get_or_create(
							user=form.user, openid=openid.openid
						)
					success_url = openid_success_url or success_url
#				print ">>>>>>>>>>>>>>>>>landing here??"
				#return render_to_response("shoppleyuser/customer_landing_page.html", context_instance=RequestContext(request))
				return HttpResponseRedirect(reverse("home"))
				#return HttpResponseRedirect(success_url)
				#return HttpResponseRedirect(reverse('home'))
	else:
		form = form_class()
#	print "request" , request.method, url_required, form.is_valid(), form.login(request), request
#	print ">>>>>>> landing there?"
	ctx = {
		"form": form,
		"url_required": url_required,
	}
	ctx.update(extra_context)
	return render_to_response(template_name, ctx,
		context_instance = RequestContext(request)
	)
@login_required
def user_profile (request):
	user = request.user
	suser = user.shoppleyuser
	#suser = ShoppleyUser.objects.get(user__id=user.id)
	if suser.is_customer():
		return HttpResponseRedirect(reverse("customer_profile"))
	else:
		return HttpResponseRedirect(reverse("merchant_profile"))
@login_required
def customer_profile(request, template="shoppleyuser/customer_profile.html"):
	user = request.user
	customer = user.shoppleyuser.customer
	#customer = Customer.objects.get(user__id=user.id)
	username = user.shoppleyuser.print_name()
	if customer.zipcode:
		zipcode = customer.zipcode.code
	else:
		zipcode = "Not given"
	address = customer.address_1
	if not address:
		address = "No address given"
	if customer.phone:
		phone = customer.phone
	else:
		phone = "Not given"
	#print customer.print_daily_limit()
	frequency = customer.print_daily_limit()
	#print frequency
	if customer.is_fb_connected:
		is_fb_connected = "1"
	else:
		is_fb_connected = "0"

	if user.emailaddress_set.count()>0:
		email = user.emailaddress_set.all()[0].email
	#print "email=", email, " or ", user.emailaddress_set.all()
	#emails = customer.emailaddress_set
		verified = user.emailaddress_set.all()[0].verified
		if verified:
		
			verified = "verified" 
		else:
			verified = "unverified" 
	else:
		email=None	
		verified=None
	return render_to_response(template, 
				{
					"username":user,
					"zipcode":zipcode,
					"address":address,
					"phone":phone,
					"frequency":frequency,
					"email":email,
					"verified":verified,
					"is_fb_connected": is_fb_connected,	
				},
				context_instance=RequestContext(request))

@login_required
def merchant_profile(request, template="shoppleyuser/merchant_profile.html"):
	user = request.user
	#merchant = Merchant.objects.get(user__id=user.id)
	merchant = user.shoppleyuser.merchant
	username = user.shoppleyuser.print_name()
#	zipcode = merchant.zipcode.code
	address = merchant.address_1
	if merchant.zipcode:
		zipcode =merchant.zipcode.code
	else:
		zipcode = "Not given"

	if merchant.phone:
		phone = merchant.phone
	else:
		phone = "Not given"

	if not address:
		address = "No address given"

	if merchant.business_name:
		business_name = merchant.business_name
	else:
		business_name = "Not given"
	if user.emailaddress_set.count()>0:
		email = user.emailaddress_set.all()[0].email
		
	#emails = merchant.emailaddress_set
		verified = user.emailaddress_set.all()[0].verified
		if verified:
			verified = "verified"
		else:
			verified = "unverified"
	else:
		email=None
		verified=None
	if merchant.is_fb_connected:
		is_fb_connected = "1"
	else:
		is_fb_connected = "0"

	return render_to_response(template, 
				{
					"username":username,
					"zipcode":zipcode,
					"address":address,
					"phone":phone,
					"business_name":business_name,
					"email":email,
					"verified":verified,
				},
				context_instance=RequestContext(request))

@login_required
def customer_profile_edit (request, form_class=CustomerProfileEditForm,
	template_name="shoppleyuser/customer_profile_edit.html", success_url=None):

	if request.method=="POST":
		form = form_class(request.POST)
		if form.is_valid():
			
			form.save(request.user.id)
			return HttpResponseRedirect(reverse("customer_profile"))
	else: 
		user = request.user
		#customer = Customer.objects.get(user__id=user.id)
		customer = user.shoppleyuser.customer
		if customer.zipcode:
			zip_code = customer.zipcode.code
		else:
			zip_code = ""
		if customer.phone:
			phone = customer.phone
		else:
			phone = ""
		
		form = form_class( initial = {'username': user.username, 
					'address1': customer.address_1,
					'zip_code': zip_code,
					'phone': phone, 
					'user_id':request.user.id,'daily_limit':customer.daily_limit,})


	ctx= {
		"form": form,
	
		}

	return render_to_response(template_name, ctx, context_instance=RequestContext(request))

@login_required
def merchant_profile_edit (request, form_class=MerchantProfileEditForm,
	template_name="shoppleyuser/merchant_profile_edit.html", success_url=None):

	if request.method=="POST":
		form = form_class(request.POST)
		if form.is_valid():
			#from django import forms

			#try:
			form.save(request.user.id)
			#except forms.ValidationError, e:
		#		print e
		#		user = request.user
		#		merchant = Merchant.objects.get(user__id=user.id)
		
#
#				return render_to_response(template_name, {"form": form_class(initial = {'username': user.username, 
 #                                       'address_1': merchant.address_1,
  #                                      'zip_code': merchant.zipcode.code,
   #                                     'phone': merchant.phone, 
    #                                    'business_name' :merchant.business_name,}), },context_instance=RequestContext(request))
			return HttpResponseRedirect(reverse("merchant_profile"))
	else: 
		user = request.user
		#merchant = Merchant.objects.get(user__id=user.id)
		merchant = user.shoppleyuser.merchant
		form = form_class( initial = {'username': user.username, 
					'address1': merchant.address_1,
					'zip_code': merchant.zipcode.code,
					'phone': merchant.phone, 
					'business_name' :merchant.business_name,
					'user_id': request.user.id,})

	ctx= {
		"form": form,		

	}
	return render_to_response(template_name, ctx, context_instance=RequestContext(request))


def merchant_signup(request, form_class=MerchantSignupForm,
	template_name="shoppleyuser/signup.html", success_url=None):

	
	success_url = "/shoppleyuser/merchant/signup-success"

	if success_url is None:
		success_url = get_default_redirect(request)
	if request.method == "POST":
		form = form_class(request.POST)
		if form.is_valid():
			username, password = form.save()
			#from shoppleyuser.utils import parse_phone_number,sms_notify
			#signup_msg = _("Wecome to Shoppley! Txt \"help\" for all commands. Enjoy!")
			#sms_notify(parse_phone_number(form.cleaned_data["phone"]),signup_msg)
			if settings.ACCOUNT_EMAIL_VERIFICATION:
				return render_to_response("account/verification_sent.html", {
					"email": form.cleaned_data["email"],
				}, context_instance=RequestContext(request))
			else:
				user = authenticate(username=username, password=password)
				auth_login(request, user)
				request.user.message_set.create(
					message=_("Successfully logged in as %(username)s.") % {
						'username': user.username
					})
				from shoppleyuser.utils import parse_phone_number,sms_notify
				signup_msg = unicode(_("Welcome to Shoppley! Txt \"#help\" for all commands. Enjoy!"))
				try:
					sms_notify(parse_phone_number(form.cleaned_data["phone"]),signup_msg)
				except ValidationError:
					pass

				return HttpResponseRedirect(success_url)
	else:
		form = form_class()
	return render_to_response(template_name, {
		"form": form,
	}, context_instance=RequestContext(request))

def customer_signup(request, form_class=CustomerSignupForm,
	template_name="shoppleyuser/customer_signup.html", success_url=None):
	#success_url = "shoopleyuser/customer_landing_page.html"

	success_url = "/shoppleyuser/customer/signup-success"

	if success_url is None:
		success_url = get_default_redirect(request)
	if request.method == "POST":
		form = form_class(request.POST)
		if form.is_valid():
			username, password = form.save()
			#from shoppleyuser.utils import parse_phone_number,sms_notify
			#signup_msg = _("Welcome to Shoppley! Txt \"#help\" for all commands. Enjoy!")
			#sms_notify(parse_phone_number(form.cleaned_data["phone"]),signup_msg)

			if settings.ACCOUNT_EMAIL_VERIFICATION:
				return render_to_response("account/verification_sent.html", {
					"email": form.cleaned_data["email"],
				}, context_instance=RequestContext(request))
			else:
				user = authenticate(username=username, password=password)
				auth_login(request, user)
				request.user.message_set.create(
					message=_("Successfully logged in as %(username)s.") % {
						'username': user.username
					})
				from shoppleyuser.utils import parse_phone_number,sms_notify
				signup_msg =unicode(_("Welcome to Shoppley! Txt \"#help\" for all commands. Enjoy!"))
				print signup_msg
				try :
					sms_notify(parse_phone_number(form.cleaned_data["phone"]),signup_msg)
				except ValidationError:
					pass

				return HttpResponseRedirect(success_url)
	else:
		form = form_class()
	return render_to_response(template_name, {
		"form": form,
	}, context_instance=RequestContext(request))

def login_modal(request):
	"""
		For simple user login
	"""

	data = {}

	username = request.POST.get("username", None)
	password = request.POST.get("password", None)
	user = authenticate(username=username, password=password)
	if user is not None:
		if user.is_active:
			auth_login(request, user)
			data["result"] = "1"
		else:
			data["result"] = "-2"
	else:
		data["result"] = "-1"

	return JSONHttpResponse(data) 


#########################################
## FOR BETA USAGE
#########################################
def customer_beta_subscribe(request, form_class=CustomerBetaSubscribeForm,
	template_name="shoppleyuser/customer_signup.html"):
	if request.method == "POST":
		redirect_url = "shoppleyuser/customer_beta_subscribe_success.html"
		form = form_class(request.POST)
		if form.is_valid():
			customer=form.save()
			data = request.POST["data"]
			try:	
				for category in data:
					customer.categories.add(Category.objects.get(tag=category))
			except:
				## signup first before choose preferences		
				pass	
			return HttpResponseRedirect(redirect_url)

	else:
		form = form_class()

	print ">>>>>>>>create form"
	return render_to_response(template_name, {
		"form": form,
		"categories": all_categories,
	}, context_instance=RequestContext(request))


