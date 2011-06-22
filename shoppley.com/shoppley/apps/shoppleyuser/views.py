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
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login

if "mailer" in settings.INSTALLED_APPS:
	from mailer import send_mail
else:
	from django.core.mail import send_mail

# Python libraries
import os, logging, simplejson
from datetime import datetime, timedelta
from common.helpers import JSONHttpResponse

from account.utils import get_default_redirect
from account.forms import LoginForm
from shoppleyuser.forms import MerchantSignupForm, CustomerSignupForm,CustomerBetaSubscribeForm
from shoppleyuser.models import Customer, ShoppleyUser



def home(request, template_name="front-page.html"):
	if request.user.is_authenticated():
		if Customer.objects.filter(user__id=request.user.id).count()>0:
			return render_to_response("shoppleyuser/customer_landing_page.html", context_instance=RequestContext(request))
		else:
			return render_to_response("shoppleyuser/merchant_landing_page.html", context_instance=RequestContext(request))
	else:
		return	render_to_response(template_name,{
					"form":CustomerSignupForm,
					"mform":MerchantSignupForm,
					"lform":LoginForm,
				},context_instance=RequestContext(request))


def account_test (request, template_name = "account/account.html"):
	try:
		shoppleyuser =ShoppleyUser.objects.get(user__id=request.user.id)	
		return render_to_response(template_name,{
					"shoppleyuser":shoppleyuser,
			}, context_instance=RequestContext(request))
	except ShoppleyUser.DoesNotExist:
		pass

def account_info(request, template_name="shoppleyuser/account_info.html"):
	try:
		shoppleyuser =ShoppleyUser.objects.get(user__id=request.user.id)
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
		customer = Customer.objects.get(user__id = request.user.id)
		return render_to_response(template_name,{
					"frequency":customer.frequency,
				}, context_instance=RequestContext(request))
	except Customer.DoesNotExist:
		pass

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
					s = ShoppleyUser.objects.get(user__id=request.user.id)
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
				signup_msg = _("Welcome to Shoppley! Txt \"#help\" for all commands. Enjoy!")
				sms_notify(parse_phone_number(form.cleaned_data["phone"]),signup_msg)

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
				signup_msg = _("Welcome to Shoppley! Txt \"#help\" for all commands. Enjoy!")
				sms_notify(parse_phone_number(form.cleaned_data["phone"]),signup_msg)


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


