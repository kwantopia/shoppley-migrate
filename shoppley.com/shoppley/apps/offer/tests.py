"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from autofixture import AutoFixture, generators
from django.test.client import Client
from django.core.urlresolvers import reverse
from datetime import datetime, timedelta
from random import randint
import json 
from mailer.models import Message
from shoppleyuser.models import *
from offer.models import *


class CustomerFixture(AutoFixture):
	class Values:
		phone = generators.IntegerGenerator(min_value=1000000000, max_value=9999999999)

class MerchantFixture(AutoFixture):
	class Values:
		phone = generators.IntegerGenerator(min_value=1000000000, max_value=9999999999)


class SimpleTest(TestCase):

	def runTest(self):
		self.client = Client()

	def setUp(self):
		# create some customers and merchants

		fixture = AutoFixture(ZipCode, generate_fk=True)
		zipcodes = fixture.create(2)

		fixture = CustomerFixture(Customer, generate_fk=True)
		customers = fixture.create(100)

		fixture = MerchantFixture(Merchant, generate_fk=True)
		merchants = fixture.create(10)

		fixture = AutoFixture(Feature)
		features = fixture.create(10)

		fixture = AutoFixture(Offer)
		offers = fixture.create(10)
		
		#fixture = AutoFixture(OfferCode)
		#offer_codes = fixture.create(100)

		for u in Customer.objects.all():
			u.user.set_password("hello")
			u.user.is_active=True
			u.user.save()

		for u in Merchant.objects.all():
			u.user.set_password("hello")
			u.user.is_active=True
			u.user.save()

	def post_json(self, command, params={}):
		print "CALL JSON", command
		response = self.client.post(command, params)
		print response
		print json.dumps(json.loads(response.content), indent=2)
		return json.loads(response.content)

	def get_json(self, command, params={}):
		print "CALL JSON", command
		response = self.client.get(command, params)
		print response
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

		self.failUnlessEqual(Merchant.objects.all().count(), 10)

		m = Merchant.objects.get(pk=105)
		self.failUnlessEqual(m.is_customer(), False)

		cmd = reverse("shoppleyuser.views.login_modal")
		params = {"username": m.user.username,
					"password": "hello"}
		response = self.post_json(cmd, params)
		self.failUnlessEqual(response["result"], "1")

		self.failUnlessEqual(m.user.is_active, True)

		success = self.client.login(username=m.user.username, password="hello")
		self.failUnlessEqual(success, True)

		later = datetime.now()+timedelta(minutes=60)		

		cmd = reverse("offer.views.test_offer")	

		params = {'name': '$10 off entrees over $30',
					'description': 'You get $10 off entrees next 90 minutes',
					'dollar_off': '10',
					'starting_time': later.strftime("%m/%d/%Y %H:%M"),
					'now': False}
		# default duration 90 minutes

		response = self.post_json( cmd, params )

		# response will be a json form, will add the response to active offers
		self.failUnlessEquals(response["result"], "1")
		offer_id1 = response["offer_id"]

		params = {'name': '5% off pants',
			'description': 'You get 5% off pants next 60 minutes',
			'percentage': '5',
			'duration': '60',
			'starting_time': later.strftime("%m/%d/%Y %H:%M"),
			'now': False}
		response = self.post_json( cmd, params )
		self.failUnlessEquals(response["result"], "1")
		offer_id2 = response["offer_id"]

		params = {'name': '$20 off dress shoes',
			'description': 'You get $20 off pants next 60 minutes',
			'dollar_off': '20',
			'duration': '70',
			'now': True}
		response = self.post_json( cmd, params )
		self.failUnlessEquals(response["result"], "1")
		offer_id3 = response["offer_id"]


		# failed offer
		params = {'name': '5% off pants',
			'description': 'You get 5% off pants next 60 minutes',
			'duration': '60',
			'now': False}
		response = self.post_json( cmd, params )
		self.failUnlessEquals(response["result"], "-1")

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

