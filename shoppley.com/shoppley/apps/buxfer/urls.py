from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from buxfer.views import *

urlpatterns = patterns('',
    url(r'^link/$', load_trans, name="link_buxfer"),
)



