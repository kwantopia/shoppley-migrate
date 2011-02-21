from googlevoice import Voice
from googlevoice.util import input
from googlevoice.extractsms import extractsms
from shoppleyuser.utils import parse_phone_number, map_phone_to_user
from django.core.management.base import NoArgsCommand
from datetime import datetime

class Command(NoArgsCommand):
    help = "Check Google Voice inbox for posted offers from merchants"
    def handle_noargs(self, **options):
		voice = Voice()
		voice.login()
		smses = voice.sms()
		to_be_deleted = []
		for msg in extractsms(voice.sms.html):
			if msg["from"] != "Me":
				su = map_phone_to_user(msg["from"])
				if su and su.is_merchant():
					details = msg["text"]
					offer = Offer(merchant=su, description=details, time_stamp=datetime.now(),
						starting_time=datetime.now()).save()
					to_be_deleted.append(msg["id"])
		for message in voice.sms().messages:
			if message.id in to_be_deleted:
				message.delete()
		
