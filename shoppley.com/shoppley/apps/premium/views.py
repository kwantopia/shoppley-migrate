# Create your views here.

import django.contrib.auth
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.db.models import Avg, Max, Min, Count
from django import forms
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.db import transaction
from django.db.models import Q
from django.conf import settings
from django.contrib import messages

if "mailer" in settings.INSTALLED_APPS:
	from mailer import send_mail
else:
	from django.core.mail import send_mail

from django.utils.translation import ugettext as _ 
from django.utils.translation import ugettext_noop

