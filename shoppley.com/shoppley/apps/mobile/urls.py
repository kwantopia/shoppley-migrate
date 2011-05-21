from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from mobile.views import *

urlpatterns = patterns('',
    url(r'^login/$', mobile_login, name="m_login"),
	url(r'^logout/$', mobile_logout, name="m_logout"),

	## customer
	url(r'^register/customer/$', register_customer, name="m_register_customer"),
	url(r'^offers/current/$', offers_current, name="m_offers_current"),
	url(r'^offers/redeemed/$', offers_redeemed, name="m_offers_redeemed"),
	url(r'^offer/forward/$', offer_forward, name="m_offer_forward"),
	url(r'^offer/feedback/$', offer_feedback, name="m_offer_feedback"),
	url(r'^offer/rate/$', offer_rate, name="m_offer_rate"),

	# points 
	url(r'^point/summary/$', point_summary, name="m_point_summary"),
	url(r'^point/offers/$', point_offers, name="m_point_offers"),

	## merchant
	url(r'^register/merchant/$', register_merchant, name="m_register_merchant"),
	url(r'^splash/$', splash_view, name="m_splash_view"),
	url(r'^offers/active/$', offers_active, name="m_offers_active"),
	url(r'^offer/start/$', offer_start, name="m_offer_start"),
	url(r'^offer/send/more/(?P<offer_id>\d+)/$', offer_send_more, name="m_offer_send_more"),
	url(r'^offer/restart/$', offer_restart, name="m_offer_restart"),
	url(r'^offer/redeem/$', offer_redeem, name="m_offer_redeem"),
	url(r'^offers/past/$', offers_past, name="m_offers_past"),
	url(r'^summary/$', merchant_summary, name="m_merchant_summary"),
	url(r'^summary/viz/$', merchant_summary_viz, name="m_merchant_summary_viz"),
	# all offers from the summary page
	url(r'^offers/all/$', offers_all, name="m_offers_all"),
	
	# points
	url(r'^point/offer/start/$', point_offer_start, name="m_point_offer_start"),
	url(r'^point/offer/(?P<offer_id>\d+)/$', point_offer, name="m_point_offer"),
	url(r'^point/offer/expire/(?P<offer_id>\d+)/$', point_offer_expire, name="m_point_offer_expire"),

)


