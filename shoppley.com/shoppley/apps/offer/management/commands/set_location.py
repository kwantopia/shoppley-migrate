from django.core.management.base import NoArgsCommand
from shoppleyuser.models import ShoppleyUser , Location
from django.contrib.sites.models import Site
from django.contrib.gis.geos import fromstr
class Command(NoArgsCommand):


	def handle_noargs(self, **options):
		
		for su in ShoppleyUser.objects.all():
			su.set_location_from_address()
