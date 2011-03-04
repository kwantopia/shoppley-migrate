"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from autofixture import AutoFixture, generators
from django.test.client import Client
from django.core.urlresolvers import reverse
from random import randint
import json 
from mailer.models import Message
from shoppleyuser.models import *
from offer.models import *
from django.contrib.auth.models import *
from datetime import datetime, timedelta

class CustomerFixture(AutoFixture):
	class Values:
		cambridge = ZipCode.objects.get(code="02139")
		phone = generators.IntegerGenerator(min_value=1000000000, max_value=9999999999)
		zipcode = cambridge

class MerchantFixture(AutoFixture):
	class Values:
		phone = generators.IntegerGenerator(min_value=1000000000, max_value=9999999999)

class SimpleTest(TestCase):

	def runTest(self):
		self.client = Client()

	def create_merchants(self):

		zip_reader = [
					["US", "02139", "Cambridge", "Massachusetts", "MA", "", "", "", "", "-42.23432", "42.23432"],
					["US", "02142", "Boston", "Massachusetts", "MA", "", "", "", "", "-42.23432", "42.23432"],
					["US", "02138", "Somerville", "Massachusetts", "MA", "", "", "", "", "-42.23432", "42.23432"]]

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

			u, created = User.objects.get_or_create(username="kool@mit.edu", email="kool@mit.edu")
			u.set_password("hello")
			u.is_active=True
			u.save()

			cambridge = ZipCode.objects.get(code="02139")
			m, created = Merchant.objects.get_or_create(user=u, address_1="15 Pearl St.",zipcode=cambridge, phone="617-234-2342", balance=100, business_name="Kwan's Pizza", admin="Kwan")
						

	def setUp(self):
		# create some customers and merchants

		#fixture = AutoFixture(ZipCode, generate_fk=True)
		#zipcodes = fixture.create(2)

		#fixture = MerchantFixture(Merchant, generate_fk=True)
		#merchants = fixture.create(10)

	
		#fixture = AutoFixture(OfferCode)
		#offer_codes = fixture.create(100)

		#for u in Merchant.objects.all():
		#	u.user.set_password("hello")
		#	u.user.is_active=True
		#	u.user.save()
		self.create_merchants()

		fixture = CustomerFixture(Customer, generate_fk=True)
		customers = fixture.create(100)

		for u in Customer.objects.all():
			u.user.set_password("hello")
			u.user.is_active=True
			u.user.save()

		fixture = AutoFixture(Feature)
		features = fixture.create(10)

		fixture = AutoFixture(Offer)
		offers = fixture.create(10)
	

	def post_json(self, command, params={}):
		print "CALL JSON", command
		response = self.client.post(command, params)
		if response.status_code == 302:
			print "Shouldn't be redirecting to: %s"%response["Location"]
		self.assertEqual(response.status_code, 200)
		print json.dumps(json.loads(response.content), indent=2)
		return json.loads(response.content)

	def get_json(self, command, params={}):
		print "CALL JSON", command
		response = self.client.get(command, params)
		if response.status_code == 302:
			print "Shouldn't be redirecting to: %s"%response["Location"]
		self.assertEqual(response.status_code, 200)
		print json.dumps(json.loads(response.content), indent=2)
		return json.loads(response.content)

	def get_web(self, command):
		print "GET CALL WEB", command
		response = self.client.get(command)
		return response 

	def post_web(self, command, params={}):
		print "CALL WEB", command
		response = self.client.post(command, params)
		return response


	def test_offer_cycle(self):
		"""
			submit some offers and check receiving of offers
			then redeem the offers
		"""

		self.failUnlessEqual(Merchant.objects.all().count(), 1)

		uname = "kool@mit.edu"
		password = "hello"

		m = Merchant.objects.get(business_name="Kwan's Pizza")
		self.failUnlessEqual(m.is_customer(), False)

		print "Authenticated:", m.user.is_authenticated()

		cmd = reverse("shoppleyuser.views.login_modal")
		params = {"username": uname, 
					"password": password}
		response = self.post_json(cmd, params)
		self.failUnlessEqual(response["result"], "1")

		self.failUnlessEqual(m.user.is_active, True)
		print m.user.get_all_permissions()
		print "Authenticated:", m.user.is_authenticated()

		success = self.client.login(username=uname, password=password)
		self.failUnlessEqual(success, True)

		later = datetime.now()+timedelta(minutes=60)		

		cmd = reverse("offer.views.test_offer")	

		params = {'name': '',
					'description': '',
					'dollar_off': '10',
					'starting_time': later.strftime("%m/%d/%Y %H:%M")
				}
		# default duration 90 minutes

		response = self.post_json( cmd, params )

		# response will be a json form, will add the response to active offers
		self.failUnlessEqual(response["result"], "-1")

		params = {'name': '$5 off the bill',
					'description': '',
					'now': True,
					'dollar_off': '5',
					'max_offers': 50,
					'duration': 90,
				}
		# default duration 90 minutes

		response = self.post_json( cmd, params )
		self.failUnlessEqual(response["result"], "1")


		params = {'name': '$10 off entrees over $30',
					'description': 'You get $10 off entrees next 90 minutes',
					'dollar_off': '10',
					'now': False,
					'starting_time': later.strftime("%m/%d/%Y %H:%M"),
					'max_offers': 50,
					'duration': 90,
				}
		# default duration 90 minutes

		response = self.post_json( cmd, params )

		# response will be a json form, will add the response to active offers
		self.failUnlessEqual(response["result"], "1")
		offer_id1 = response["offer_id"]
		print "Offer 1 sent to:", response["num_sent"]

		params = {'name': '5% off pants',
			'description': 'You get 5% off pants next 60 minutes',
			'percentage': '5',
			'duration': '60',
			'starting_time': later.strftime("%m/%d/%Y %H:%M"),
					'max_offers': 50,
					'duration': 90,
			'now': False}
		response = self.post_json( cmd, params )
		self.failUnlessEqual(response["result"], "1")
		offer_id2 = response["offer_id"]
		print "Offer 2 sent to:", response["num_sent"]

		params = {'name': '$20 off dress shoes',
			'description': 'You get $20 off pants next 60 minutes',
			'dollar_off': '20',
			'duration': '70',
			'max_offers': 50,
			'now': True}
		response = self.post_json( cmd, params )
		self.failUnlessEqual(response["result"], "1")
		offer_id3 = response["offer_id"]
		print "Offer 3 sent to:", response["num_sent"]


		# failed offer, no money specified
		params = {'name': '5% off pants',
			'description': 'You get 5% off pants next 60 minutes',
			'duration': '60',
			'now': False}
		response = self.post_json( cmd, params )
		self.failUnlessEqual(response["result"], "-1")

		# check if offers generated
		offers1 = OfferCode.objects.filter(offer=offer_id1).count()
		self.failIfEqual(offers1, 0)		

		# check if offers generated
		offers2 = OfferCode.objects.filter(offer=offer_id2).count()
		self.failIfEqual(offers2, 0)		
	
		# check if offers generated
		offers3 = OfferCode.objects.filter(offer=offer_id3).count()
		self.failIfEqual(offers3, 0)		
		

	def test_basic_addition(self):
		"""
		Tests that 1 + 1 always equals 2.
		"""
		self.failUnlessEqual(1 + 1, 2)

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

