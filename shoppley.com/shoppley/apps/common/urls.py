from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from common.views import *

urlpatterns = patterns('',
	url(r'^survey/$', direct_to_template, {"template": "common/init_survey.html"}, name="init_survey"),
)



