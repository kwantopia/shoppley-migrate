from django.conf.urls.defaults import *
from instantmessage.views import *

urlpatterns = patterns('',
    url(r'^index.json$', index, name="im_index"),
	url(r'^verify_yes$', verify_yes, name="im_verify_yes"),
	url(r'^verify_no$', verify_no, name="im_verify_no"),
)
