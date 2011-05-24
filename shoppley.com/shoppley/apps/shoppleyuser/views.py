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
from shoppleyuser.forms import MerchantSignupForm, CustomerSignupForm

def login(request, form_class=LoginForm, template_name="account/login.html",
			success_url=None, associate_openid=False, openid_success_url=None,
			url_required=False, extra_context=None):
	if extra_context is None:
		extra_context = {}
	if success_url is None:
		success_url = get_default_redirect(request)
	if request.method == "POST" and not url_required:
		form = form_class(request.POST)
		if form.is_valid():
			if form.login(request):
				if associate_openid and association_model is not None:
					for openid in request.session.get('openids', []):
						assoc, created = UserOpenidAssociation.objects.get_or_create(
							user=form.user, openid=openid.openid
						)
					success_url = openid_success_url or success_url
				return HttpResponseRedirect(success_url)
	else:
		form = form_class()
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
	if success_url is None:
		success_url = get_default_redirect(request)
	if request.method == "POST":
		form = form_class(request.POST)
		if form.is_valid():
			username, password = form.save()
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
				return HttpResponseRedirect(success_url)
	else:
		form = form_class()
	return render_to_response(template_name, {
		"form": form,
	}, context_instance=RequestContext(request))

def customer_signup(request, form_class=CustomerSignupForm,
	template_name="shoppleyuser/customer_signup.html", success_url=None):
	if success_url is None:
		success_url = get_default_redirect(request)
	if request.method == "POST":
		form = form_class(request.POST)
		if form.is_valid():
			username, password = form.save()
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
