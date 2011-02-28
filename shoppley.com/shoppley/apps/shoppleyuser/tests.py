from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from datetime import datetime, timedelta
from random import randint
from shoppleyuser.models import *
import json 
from mailer.models import Message

class SimpleTest(TestCase):
	
	fixtures = ['']

	def runTest(self):
		self.client = Client()

	def setUp(self):
		# create some zip codes 
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

	def test_user_account_create(self):

		cmd = reverse("customer_signup")
		params = {"email": "kool@mit.edu",
					"password1": "hello",
					"password2": "hello",
					"confirmation_key": "",
					"address_1": "02139",
					"address_2": "",
					"zip_code": "02142",
					"phone": "617-909-2101"}

		response = self.post_web(cmd, params)
		print response.content
		self.failUnlessEqual(Message.objects.filter(to_address="kool@mit.edu").count(), 1) 

	
