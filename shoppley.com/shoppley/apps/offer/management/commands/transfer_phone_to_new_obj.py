from django.core.management.base import NoArgsCommand
from shoppleyuser.models import CustomerPhone, MerchantPhone, ShoppleyUser

class Command(NoArgsCommand):

	def handle_noargs(self, **options):
		for su in ShoppleyUser.objects.all():
			if su.is_customer():
				p, created = CustomerPhone.objects.get_or_create(customer = su.customer, number = su.phone)
			else:
				p, created = MerchantPhone.objects.get_or_create(merchant = su.merchant, number = su.phone)
			print created, p
