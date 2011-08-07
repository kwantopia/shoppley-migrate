from django import template
from django.conf import settings
from offer.models import Offer, OfferCode
from shoppleyuser.utils import pretty_date
from offer.utils import pretty_datetime
register = template.Library()

@register.inclusion_tag("offer/customer_offer_tag.html")
def customer_offer_tag(offer):
	return {"title": offer.title,
		"description": offer.description,
		"location": offer.merchant.print_address(),
		"biz_name" : offer.merchant.business_name,
		"time_left": pretty_date(offer.expired_time, True),
		"STATIC_URL": settings.STATIC_URL,
	}

@register.inclusion_tag("offer/customer_offer_tag.html")
def customer_offercode_tag(offercode):
	offer = offercode.offer
	return {"title": offer.title,
                "description": offer.description,
                "location": offer.merchant.print_address(),
                "biz_name" : offer.merchant.business_name,
                "time_left": pretty_date(offer.expired_time, True),
                "STATIC_URL": settings.STATIC_URL,
	}

@register.inclusion_tag("offer/customer_offer_side_tag.html")
def customer_offer_side_tag(offer):
	offer = offercode.offer
	return {
		"title": offer.title,
		"description": offer.description,
		"location": offer.merchant.print_address(),
		"biz_name" : offer.merchant.business_name,
		"time_left": pretty_date(offer.expired_time, True),
		"STATIC_URL": settings.STATIC_URL,
		#"redeem_time": pretty_datetime(offer.redeem_time),
	}

@register.inclusion_tag("offer/customer_offer_side_tag.html")
def customer_offercode_side_tag(offercode):
	offer = offercode.offer
	return {
		"title": offer.title,
                "description": offer.description,
                "location": offer.merchant.print_address(),
                "biz_name" : offer.merchant.business_name,
                "time_left": pretty_date(offer.expired_time, True),
                "STATIC_URL": settings.STATIC_URL,
                "redeem_time": pretty_datetime(offercode.redeem_time),

	}

@register.inclusion_tag("offer/merchant_offer_tag.html")
def merchant_offer_tag(offer):
	duration = offer.duration
	init_sent = offer.num_init_sentto
	forwarded = offer.offercode_set.filter(forwarder__isnull=False).count()
	redeemed = offer.offercode_set.filter(redeem_time__isnull=False).count()
	return {"title": offer.title,
                "description": offer.description,
		"init_sent": init_sent,
		"forwarded": forwarded,
		"redeemed": redeemed,
                "time_left": pretty_date(offer.expired_time, True),
                "STATIC_URL": settings.STATIC_URL,
	}


@register.inclusion_tag("offer/merchant_offer_side_tag.html")
def merchant_offer_side_tag(offer):
	duration = offer.duration
	init_sent = offer.num_init_sentto
	forwarded = offer.offercode_set.filter(forwarder__isnull=False).count()
	redeemed = offer.offercode_set.filter(redeem_time__isnull=False).count()
	return {"title": offer.title,
		"description": offer.description,
		"init_sent": init_sent,
		"forwarded": forwarded,
		"redeemed": redeemed,
		"time_left": pretty_date(offer.expired_time, True),
		"STATIC_URL": settings.STATIC_URL,
	}


@register.inclusion_tag("offer/merchant_offer_side_tag.html")
def merchant_offercode_side_tag(offercode):
	offer = offercode.offer
	duration = offer.duration
	init_sent = offer.num_init_sentto
	forwarded = offer.offercode_set.filter(forwarder__isnull=False).count()
	redeemed = offer.offercode_set.filter(redeem_time__isnull=False).count()
	return {"title": offer.title,
		"description": offer.description,
		"init_sent": init_sent,
		"forwarded": forwarded,
		"redeemed": redeemed,
		"time_left": pretty_date(offer.expired_time, True),
		"STATIC_URL": settings.STATIC_URL,
	}

@register.inclusion_tag("offer/merchant_offer_tag.html")
def merchant_offercode_tag(offercode):
	offer = offercode.offer
	duration = offer.duration
	init_sent = offer.num_init_sentto
	forwarded = offer.offercode_set.filter(forwarder__isnull=False).count()
	redeemed = offer.offercode_set.filter(redeem_time__isnull=False).count()
	return {"title": offer.title,
	        "description": offer.description,
	        "init_sent": init_sent,
	        "forwarded": forwarded,
	        "redeemed": redeemed,
	        "time_left": pretty_date(offer.expired_time, True),
	        "STATIC_URL": settings.STATIC_URL,
	}

