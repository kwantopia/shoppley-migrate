from django.core.management.base import NoArgsCommand
from shoppleyuser.models import *

class Command(NoArgsCommand):

	help = 'Resets the offer counts for the customers to 0 so they can receive new offers.'

	def handle_noargs(self, **options):
		for u in ShoppleyUser.objects.all():
			if u.is_customer():
				u.customer.offer_count=0
				u.customer.save()
		print "Offer count for all users reset to 0"
