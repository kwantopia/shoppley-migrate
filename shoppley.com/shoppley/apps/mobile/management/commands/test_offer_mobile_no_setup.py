from django.core.management.base import NoArgsCommand
from mobile.tests import SimpleTest

class Command(NoArgsCommand):
	def handle_noargs(self, **options):
		s = SimpleTest()
		s.create_test_offers()
