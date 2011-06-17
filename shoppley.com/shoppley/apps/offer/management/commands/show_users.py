from django.core.management.base import NoArgsCommand
from shoppleyuser.models import *

class Command(NoArgsCommand):

	help = "Shows the current status of users."

	def handle_noargs(self, **options):
		print "ID", "email", "phone", "merchant", "verified", "offer_count", "daily_limit"
		for u in ShoppleyUser.objects.all():
			if u.is_customer():
				print "customer", u.id, u.user.email, u.phone, u.is_merchant(), u.verified, u.customer.offer_count, u.customer.daily_limit
			else:
				print "merchant",u.id, u.user.email, u.phone, u.is_merchant(), u.verified 
