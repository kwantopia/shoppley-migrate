from django.core.management.base import NoArgsCommand
from shoppleyuser.models import ShoppleyUser , Location
from django.contrib.sites.models import Site
from django.contrib.gis.geos import fromstr
class Command(NoArgsCommand):


	def handle_noargs(self, **options):
		from shoppleyuser.utils import get_lat_long
		for su in ShoppleyUser.objects.all():
			latlon = get_lat_long(su.address_1 + " "+su.zipcode.code)
			try:
				l, created = Location.objects.get_or_create(location=fromstr("POINT(%s %s)" % (latlon[0], latlon[1])))
			except Location.MultipleObjectsReturned:
				l = Location.objects.filter(location=fromstr("POINT(%s %s)" % (latlon[0], latlon[1])))[0]
			su.location = l
			su.save()
