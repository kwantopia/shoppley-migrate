from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from premium.views import *

urlpatterns = patterns('',
	url(r'^survey/$', direct_to_template, {"template": "premium/survey.html"}, name="premium_beta_survey"),
)



