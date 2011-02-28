from django.core.management.base import NoArgsCommand
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext, string_concat
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.conf import settings

from shoppleyuser.utils import parse_phone_number, map_phone_to_user, sms_notify, sms_notify_list
from shoppleyuser.models import Customer
from offer.models import Offer, OfferCode
from googlevoice import Voice
from googlevoice.util import input
from googlevoice.extractsms import extractsms

from datetime import datetime
import re

pattern = "([\w]{%d})[ ]+\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})") % (settings.OFFER_CODE_LENGTH)
redemption_code_re = re.compile(pattern)

class Command(NoArgsCommand):
	help = "Check Google Voice inbox for posted offers from merchants"
	def handle_noargs(self, **options):
		voice = Voice()
		voice.login()
		smses = voice.sms()
		for msg in extractsms(voice.sms.html):
			print "new message %s" % msg
			if msg["from"] != "Me":
				su = map_phone_to_user(msg["from"])
				if su and su.is_merchant():
					text = msg["text"].strip()
					if redemption_code_re.search(text):
						n = redemption_code_re.search(text)
						offer_code = n.group(1) 
						phone = n.group(2) + n.group(3) + n.group(4)
						try:
							current_time = datetime.now()
							offercode_obj = OfferCode.objects.filter(expiration_time__gt=current_time, 
								time_stamp__lt=current_time).get(code__iexact=offer_code)
							# The offer code is a valid code, but it might come from referrals
							try:
								# Does the phone belong to a registered customer?
								customer = Customer.objects.get(phone__contains=phone)
								if offercode_obj.customer == customer:
									if not offercode_obj.redeem_time:
										offercode_obj.redeem_time = current_time
										offercode_obj.save()
										receipt_msg = _("%(offer_code)s is a valid offer code! Redeemed by %(customer)s.") % {
											"offer_code": offer_code,
											"customer": offercode_obj.customer
										}
										sms_notify(su.phone, receipt_msg)
									else:
										receipt_msg = _("Code reuse! %(offer_code)s was redeemed by %(customer)s at %(time)s.") % {
											"offer_code": offer_code,
											"customer": offercode_obj.customer,
											"time": offercode_obj.redeem_time,
										}
										sms_notify(su.phone, receipt_msg)
										# TODO Save the reuse behaviors
								else:
									receipt_msg = _("Code referral! %(offer_code)s was transferred from %(sender)s to %(receiver)s.") % {
										"offer_code": offer_code,
										"sender": offercode_obj.customer,
										"receiver": customer,
									}
									sms_notify(su.phone, receipt_msg)
									#TODO Save the referral information
							except ObjectDoesNotExist:
								# Such phone number doesn't exist in customers' profiles, save it
								receipt_msg = _("Code referral! %(offer_code)s was transferred from %(sender)s to %(phone)s.") % {
									"offer_code": offer_code,
									"sender": offercode_obj.customer,
									"phone": phone,
								}
								sms_notify(su.phone, receipt_msg)
								#TODO Save the referral information
							except MultipleObjectsReturned, e:
								# Multiple customers registered with the same phone number, should be prevented
								print e
								
						except ObjectDoesNotExist:
							# The offer code is not found, or an invalid one
							receipt_msg = _("%(offer_code)s is not a valid offer code!") % {
								"offer_code": offer_code,
							}
							sms_notify(su.phone, receipt_msg)
						except MultipleObjectsReturned, e:
							# Multiple offer codes found, which indicates a programming error
							print e
					else:
						# This is an offer, not a redeption code
						offer = Offer(merchant=su.merchant, name=text[:128],
							description=text, time_stamp=datetime.now(),
							starting_time=datetime.now())
						offer.save()
						offer.distribute()
						receipt_msg = _("We have received your offer message, %(number)d users have been reached") % {
							"number": offer.num_received(),
						}
						sms_notify(su.phone, receipt_msg)
				else:
					# TODO: We should save all messages
					pass
		for message in voice.sms().messages:
			message.delete()
	
