from googlevoice import Voice
from googlevoice.util import input
from googlevoice.extractsms import extractsms
from shoppleyuser.utils import parse_phone_number, map_phone_to_user, sms_notify, sms_notify_list
from offer.models import Offer, OfferCode
from django.core.management.base import NoArgsCommand
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext, string_concat
from django.conf import settings
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
	
