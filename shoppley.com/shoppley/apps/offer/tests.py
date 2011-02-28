"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from autofixture import AutoFixture
from django.test.client import Client
from django.core.urlresolvers import reverse
from datetime import datetime, timedelta
from random import randint
import json 
from mailer.models import Message



class SimpleTest(TestCase):

	def runTest(self):
		self.client = Client()

	def setUp(self):
		fixture = AutoFixture(Feature, generate_fk=True)
		features = fixture.create(10)

		fixture = AutoFixture(Offer, generate_fk=True)
		offers = fixture.create(10)
		
		fixture = AutoFixture(OfferCode, generate_fk=True)
		offer_codes = fixture.create(100)

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

		cmd = reverse("offer.views.start_offer")	

		params = {'name': '$10 off entrees over $30',
					'description': 'You get $10 off entrees next 90 minutes',
					'dollar_off': '10'}
		# default duration 90 minutes

		response = post_json( cmd, params )
		# response will be a json form, will add the response to active offers
		self.failUnlessEquals(response["result"], "1")
		offer_id1 = response["offer_id"]

		params = {'name': '5% off pants',
			'description': 'You get 5% off pants next 60 minutes',
			'percentage': '5',
			'duration': '60'}
		response = post_json( cmd, params )
		self.failUnlessEquals(response["result"], "1")
		offer_id2 = response["offer_id"]

		# failed offer
		params = {'name': '5% off pants',
			'description': 'You get 5% off pants next 60 minutes',
			'duration': '60'}
		response = post_json( cmd, params )
		self.failUnlessEquals(response["result"], "-1")

		# check if offers generated
		offers1 = OfferCode.objects.filter(offer=offer_id1).count()
		
		# check if offers generated
		offers2 = OfferCode.objects.filter(offer=offer_id2).count()
	
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

