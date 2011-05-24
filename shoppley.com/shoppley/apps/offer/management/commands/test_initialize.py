from django.core.management.base import NoArgsCommand
from shoppleyuser.models import *

class Command(NoArgsCommand):
	def handle_noargs(self, **options):
		c, created = Country.objects.get_or_create( name="United States", code="US")
		r, created = Region.objects.get_or_create(name="Massachusetts", code="MA", country=c)
		city, created = City.objects.get_or_create(name="Boston", region=r)
		zipcode, created = ZipCode.objects.get_or_create(code="02142", city=city)
		zipcode, created = ZipCode.objects.get_or_create(code="02139", city=city)
		u, created = User.objects.get_or_create(username="kool2@mit.edu", first_name="Kwan2", last_name="Lee2", email="kool2@mit.edu")
		u.set_password("hello")
		u.save()
		shop_merchant, created = Merchant.objects.get_or_create(user=u, address_1="15 Pearl St.", zipcode = zipcode, phone="617-871-0710", business_name="Kwan's Pizza", admin="Jake Foster" )
		
		u, created = User.objects.get_or_create(username="kool@mit.edu", first_name="Kwan", last_name="Lee", email="kool@mit.edu")
		u.set_password("hello")
		u.save()
		shop_user, created = Customer.objects.get_or_create(user=u, address_1="20 Pearl St. apt 1", zipcode = zipcode, phone="617-909-2101" )
		shop_user.merchant_likes.add(shop_merchant)

