from django.core.management.base import NoArgsCommand
from shoppleyuser.models import *
from django.contrib.sites.models import Site
class Command(NoArgsCommand):


	def handle_noargs(self, **options):
		# create users merchants and zipcodes
		c, created = Country.objects.get_or_create( name="United States", code="US")
		r, created = Region.objects.get_or_create(name="Massachusetts", code="MA", country=c)
		city, created = City.objects.get_or_create(name="Boston", region=r)
		zipcode, created = ZipCode.objects.get_or_create(code="02142", city=city)
		zipcode, created = ZipCode.objects.get_or_create(code="02139", city=city)
		u, created = User.objects.get_or_create(username="kool2@mit.edu", first_name="Kwan2", last_name="Lee2", email="kool2@mit.edu")
		u.set_password("hello")
		u.save()
		shop_merchant, created = Merchant.objects.get_or_create(user=u, address_1="15 Pearl St.", zipcode = zipcode, phone="6178710710", business_name="Kwan's Pizza", admin="Jake Foster" )
		
		u, created = User.objects.get_or_create(username="kool@mit.edu", first_name="Kwan", last_name="Lee", email="kool@mit.edu")
		u.set_password("hello")
		u.save()
		shop_user, created = Customer.objects.get_or_create(user=u, address_1="20 Pearl St. apt 1", zipcode = zipcode, phone="6179092101" )
		shop_user.merchant_likes.add(shop_merchant)

		shoppley, created = Site.objects.get_or_create(name="Shoppley", domain="shoppley.com")
		webuy, created = Site.objects.get_or_create(name="Shoppley", domain="webuy-dev.mit.edu")

		# create categories
		categories = [("Dining & Nightlife", "dining"), ("Health & Beauty", "health"), ("Fitness","fitness"), ("Retail & Services", "retail"), ("Activities & Events", "activities"), ("Special Interests", "special")]
		for cat in categories:
			category, created = Category.objects.get_or_create(name=cat[0], tag=cat[1])
		
