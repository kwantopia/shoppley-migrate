from django.core.management.base import NoArgsCommand
from django.contrib.sites.models import Site

from mobile.tests import SimpleTest

class Command(NoArgsCommand):
	def handle_noargs(self, **options):
		s = SimpleTest()
		s.setUp()
		s.create_test_offers()

		shoppley, created = Site.objects.get_or_create(name="Shoppley", domain="shoppley.com") 
		webuy, created = Site.objects.get_or_create(name="Shoppley", domain="webuy-dev.mit.edu")


