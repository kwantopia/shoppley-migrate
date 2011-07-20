from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from mobile.views import *

urlpatterns = patterns('',
    url(r'^login/$', mobile_login, name="m_login"),
	url(r'^logout/$', mobile_logout, name="m_logout"),

	## customer
	url(r'^customer/register/$', register_customer, name="m_register_customer"),
	url(r'^customer/offers/current/$', offers_current, name="m_offers_current"),
	url(r'^customer/offers/current/filter/$', offers_current_filter, name="m_offers_current_filter"),
	url(r'^customer/offers/redeemed/$', offers_redeemed, name="m_offers_redeemed"),
	url(r'^customer/offer/offercode/$', offer_get_offercode, name="m_offer_offercode"),
	url(r'^customer/offer/forward/$', offer_forward, name="m_offer_forward"),
	url(r'^customer/offer/feedback/$', offer_feedback, name="m_offer_feedback"),
	url(r'^customer/offer/rate/$', offer_rate, name="m_offer_rate"),

	# points 
	url(r'^customer/point/summary/$', customer_point_summary, name="m_customer_point_summary"),
	url(r'^customer/point/offers/$', customer_point_offers, name="m_customer_point_offers"),

	## merchant
	url(r'^merchant/register/$', register_merchant, name="m_register_merchant"),
	url(r'^merchant/splash/$', splash_view, name="m_splash_view"),
	url(r'^merchant/offers/active/$', offers_active, name="m_offers_active"),
	url(r'^merchant/offer/start/$', offer_start, name="m_offer_start"),
	url(r'^merchant/offer/send/more/(?P<offer_id>\d+)/$', offer_send_more, name="m_offer_send_more"),
	url(r'^merchant/offer/restart/(?P<offer_id>\d+)/$', offer_restart, name="m_offer_restart"),
	url(r'^merchant/offer/redeem/$', offer_redeem, name="m_offer_redeem"),
	url(r'^merchant/offers/past/(?P<days>\d+)/$', offers_past, name="m_offers_past"),
	url(r'^merchant/summary/$', merchant_summary, name="m_merchant_summary"),
	url(r'^merchant/summary/viz/$', merchant_summary_viz, name="m_merchant_summary_viz"),
	# point offers
	url(r'^merchant/point/offers/active/$', point_offers_active, name="m_point_offers_active"),
	url(r'^merchant/point/offers/past/$', point_offers_past, name="m_point_offers_past"),
	url(r'^merchant/point/offer/start/$', point_offer_start, name="m_point_offer_start"),
	url(r'^merchant/point/offer/restart/$', point_offer_restart, name="m_point_offer_restart"),
	url(r'^merchant/point/offer/expire/(?P<offer_id>\d+)/$', point_offer_expire, name="m_point_offer_expire"),

)


