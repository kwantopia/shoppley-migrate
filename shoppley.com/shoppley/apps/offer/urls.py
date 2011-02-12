from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from offer.views import *

urlpatterns = patterns('',
    url(r'^$', offer_home, name="offer_home"),
)


