from django.core.management.base import NoArgsCommand
from django.contrib.sites.models import Site

from shoppleyuser.models import Country, Region, City, ZipCode, ShoppleyUser
import os, csv
from googlevoice import Voice

FILE_ROOT = os.path.abspath(os.path.dirname(__file__))

class Command(NoArgsCommand):
	def handle_noargs(self, **options):
		f = open(FILE_ROOT+"/../../../shoppleyuser/data/US.txt", "r")
		zip_reader = csv.reader(f, delimiter="\t")
		for row in zip_reader:
			country_obj, created = Country.objects.get_or_create(name="United States", code=row[0])
			zip_code = row[1]
			city = row[2]
			region = row[3]
			region_code = row[4]
			latitude = row[9]
			longitude = row[10]
			region_obj, created = Region.objects.get_or_create(name=region,
						code=region_code, country=country_obj)
			city_obj, created = City.objects.get_or_create(name=city, region=region_obj)
			zip_obj, created = ZipCode.objects.get_or_create(code=zip_code,
						city=city_obj, latitude=latitude, longitude=longitude)

		shoppley, created = Site.objects.get_or_create(name="Shoppley", domain="shoppley.com")
		webuy, created = Site.objects.get_or_create(name="Shoppley", domain="webuy-dev.mit.edu")
		print "done"
