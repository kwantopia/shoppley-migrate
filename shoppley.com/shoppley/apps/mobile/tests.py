"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
import csv, json
import pprint
from django.contrib.auth.models import User
from shoppleyuser.models import ShoppleyUser, Country, Region, City, ZipCode, Merchant, Customer
import sqlite3, random
from datetime import datetime

from offer.models import Offer, OfferCode

class SimpleTest(TestCase):

	def runTest(self):
		pass

	def setUp(self):
		self.pp = pprint.PrettyPrinter(indent=2)

		us, created = Country.objects.get_or_create(name="United States", code="us")
		region, created = Region.objects.get_or_create(name="Massachusetts", code="ma", country=us)
		city, created = City.objects.get_or_create(name="Cambridge", region=region)
		zipcode1, created = ZipCode.objects.get_or_create(code="02139", city=city)
		city, created = City.objects.get_or_create(name="Boston", region=region)
		zipcode2, created = ZipCode.objects.get_or_create(code="02250", city=city)

		# create users
		u, created = User.objects.get_or_create(username="user1@customer.com")
		u.email="user1@customer.com"
		u.set_password("hello")
		u.save()
		
		c, created = Customer.objects.get_or_create(user=u, address_1="", address_2="", zipcode=zipcode1, phone="617-682-9602", balance=1000)
		
		u, created = User.objects.get_or_create(username="user2@customer.com")
		u.email="user2@customer.com"
		u.set_password("hello")
		u.save()
		
		c, created = Customer.objects.get_or_create(user=u, address_1="15 Franklin St.", address_2="", zipcode=zipcode1, phone="617-871-0710", balance=1000)

		u, created = User.objects.get_or_create(username="user3@customer.com")
		u.email="user3@customer.com"
		u.set_password("hello")
		u.save()
		
		#617-453-8665 Meng's googlevoice number
		c, created = Customer.objects.get_or_create(user=u, address_1="15 Franklin St.", address_2="", zipcode=zipcode2, phone="617-453-8665", balance=1000)

		u, created = User.objects.get_or_create(username="user1@merchant.com")
		u.email="user1@merchant.com"
		u.set_password("hello")
		u.save()

		
		m, created = Merchant.objects.get_or_create(user=u, address_1="", address_2="", zipcode=zipcode1, phone="617-682-9784", balance=10000, business_name="Dunkin Donuts", admin="Jake Sullivan", url="http://www.shoppley.com")

		u, created = User.objects.get_or_create(username="user2@merchant.com")
		u.email="user2@merchant.com"
		u.set_password("hello")
		u.save()

		m, created = Merchant.objects.get_or_create(user=u, address_1="190 Mass Av.", address_2="", zipcode=zipcode1, phone="617-909-2101", balance=10000, business_name="Flour Bakery", admin="John Jacobson", url="http://www.shoppley.com")

	def post_json(self, command, params={}, comment="No comment", redirect=False):
		print "*"*100
		print comment
		print "-"*100
		print "POST URL:", command
		print "PARAMS:"
		self.pp.pprint(params) 
		response = self.client.post(command, params)
		print "-"*100
		print "RESPONSE:"
		if redirect:
			if response.status_code == 302:
				print "Should be redirecting to: %s"%response["Location"]
				return "Redirect to:",response["Location"]
			else:
				return "Response code:", response.status_code
		else:
			self.assertEqual(response.status_code, 200)
		print json.dumps(json.loads(response.content), indent=2)
		return json.loads(response.content)

	def get_json(self, command, params={}, comment="No comment", redirect=False):
		print "*"*100
		print comment
		print "-"*100
		print "GET URL:", command
		print "PARAMS:"
		self.pp.pprint(params)
		response = self.client.get(command, params)
		#print response
		print "-"*100
		print "RESPONSE:"
		if redirect:
			if response.status_code == 302:
				print "Should be redirecting to: %s"%response["Location"]
				return "Redirect to:",response["Location"]
			else:
				return "Response code:", response.status_code
		else:
			self.assertEqual(response.status_code, 200)
		print json.dumps(json.loads(response.content), indent=2)
		return json.loads(response.content)

	def get_web(self, command, params={}, comment="No comment"):
		print "*"*100
		print comment
		print "-"*100
		print "GET WEB URL", command
		print "PARAMS:" 
		self.pp.pprint(params)
		response = self.client.get(command, params)
		return response

	def post_web(self, command, params={}, comment="No comment"):
		print "*"*100
		print comment
		print "-"*100
		print "POST WEB URL", command
		print "PARAMS:" 
		self.pp.pprint(params)
		response = self.client.post(command, params)
		return response

	def create_test_offers(self):
		"""
			Generate several offers by multiple merchants that targets two different users in two different
			zip codes
		"""
	
		offers = ["$5 off shoes brands, Nike, Reebok"] #,
				#"15% off big steak and 10% off small steak",
				#				"Save $15 on your purchase of suit",
				#				"$125 for tonight only at Marriott"]

		m = Merchant.objects.get(user__email="user1@merchant.com")	
		for o in offers:
			offer = Offer(merchant=m, title=o[:40], description=o, time_stamp=datetime.now(), starting_time=datetime.now()) 
			offer.save()
			offer.distribute()

		assert offer.offercode_set.all().count()==2

		offers = ["$1 off Chicken Sandwiches",
				"Free drink when you order $10 or more",
								"Half priced cookies"]

		m = Merchant.objects.get(user__email="user2@merchant.com")	
		for o in offers:
			offer = Offer(merchant=m, title=o[:40], description=o, time_stamp=datetime.now(), starting_time=datetime.now()) 
			offer.save()
			offer.distribute()

		assert offer.offercode_set.all().count()==2

	def redeem_offer(self):
		"""
			Redeems an offer of user1@customer.com 
		"""

		u = User.objects.get(email="user1@customer.com")
		c = u.shoppleyuser.customer
		o = random.sample( OfferCode.objects.filter(customer=c), 1 )
		o[0].redeem()

	def random_offer(self):

		u = User.objects.get(email="user1@customer.com")
		c = u.shoppleyuser.customer
		
		while o.redeem_time != None:
			o = random.sample( OfferCode.objects.filter(customer=c), 1 )

		return o

	def test_mobile_api(self):
		"""
			Generate mobile API doc as it tests
		"""

		self.create_test_offers()

		email = "user1@customer.com"
		password = "hello"

		comment = "Customer login"
		response = self.post_json( reverse("m_login"), {'email': email,
													'password': password}, comment)

		"""
		if self.client.login(username=email, password=password):
			print "Login successful"
		else:
			print "Login failed"
		"""
		
		comment = "Show current offers, it also returns offer details"
		response = self.post_json( reverse("m_offers_current"), {'lat':47.78799, 'lon':98.99890}, comment)

		offer_code_to_forward = response["offers"][1]["code"]

		comment = "Show narrow geographical offers, st also returns offer details"
		response = self.post_json( reverse("m_offers_current"), {'lat':47.78799, 'lon':98.99890}, comment)

		self.redeem_offer()
		comment = "Show redeemed offers, it also returns offer details"
		response = self.get_json( reverse("m_offers_redeemed"), {}, comment)

		comment = "Forward offer to a list of phone numbers"
		response = self.post_json( reverse("m_offer_forward"), {'offer_code': offer_code_to_forward,'phones':['617-877-2345', '857-678-7897', '617-871-0710', '617-453-8665'], 'note': 'This offer might interest you.'}, comment)

		comment = "Provide feedback on an offer"
		response = self.post_json( reverse("m_offer_feedback"), {'feedback':'The fish dish was amazing'}, comment)

		comment = "Rate an offer 1-5, 0 if unrated"
		response = self.post_json( reverse("m_offer_rate"), {'rating':5}, comment)

		# test points
		comment = "Shows a summary of accumulated points for customer"
		response = self.get_json( reverse("m_customer_point_summary"), {}, comment)

		comment = "Shows a list of point offers one can use to redeem (details too)"
		response = self.get_json( reverse("m_customer_point_offers"), {}, comment)

		comment = "Customer logout"
		response = self.get_json( reverse("m_logout"), {}, comment)
					
		email = "user3@customer.com"
		password = "hello"

		comment = "Customer login"
		response = self.post_json( reverse("m_login"), {'email': email,
													'password': password}, comment)

		comment = "Show current offers, it also returns offer details (This one contains offer forwarded by another customer)"
		response = self.post_json( reverse("m_offers_current"), {'lat':47.78799, 'lon':98.99890}, comment)


		comment = "Customer logout"
		response = self.get_json( reverse("m_logout"), {}, comment)
	
		email = "user4@customer.com"
		password = "hello"

		comment = "Customer registration"
		response = self.post_json( reverse("m_register_customer"), {'email': email, 'phone': '617-885-2347', 'zipcode': '02139'}, comment)
	
		comment = "Customer logout"
		response = self.get_json( reverse("m_logout"), {}, comment, redirect=True)

		email = "user1@merchant.com"
		password = "hello"

		comment = "Merchant login"
		response = self.post_json( reverse("m_login"), {'email': email,
													'password': password}, comment)
	
		comment = "Splash view for the merchant"
		response = self.get_json( reverse("m_splash_view"), {}, comment)

		comment = "Show active offers for the merchant, returns offer details"
		response = self.get_json( reverse("m_offers_active"), {}, comment)
		
		comment = "Start a % off offer (units=0), duration if not specified will be next 60 minutes"
		response = self.post_json( reverse("m_offer_start"), {
								'title':'10% off on entree',
								'description': 'Come taste some great greek food next 30 minutes',
								'now': False,
								'date': '2011-05-18',
								'time': '06:00:00 PM',
								'duration': 60,
								'units': 0,
								'amount': 10 }, comment)
				
		comment = "Start a $ off offer (units=1), duration if not specified will be next 60 minutes"
		response = self.post_json( reverse("m_offer_start"), {
								'title':'$10 off on entree',
								'description': 'Come taste some great greek food next 30 minutes',
								'now': False,
								'date': '2011-05-18',
								'time': '06:00:00 PM',
								'duration': 30,
								'units': 1,
								'amount': 10 }, comment)

		comment = "Start a $ off offer NOW (units=1), duration if not specified will be next 60 minutes"
		response = self.post_json( reverse("m_offer_start"), {
								'title':'$10 off on entree',
								'description': 'Come taste some great greek food next 30 minutes',
								'now': True,
								'duration': 90,
								'units': 1,
								'amount': 10 }, comment)

		comment = "Send more of the same offer"
		response = self.get_json( reverse("m_offer_send_more", args=[response['offer_id']]), {}, comment) 

		comment = "Restart a previous offer (it allows change of parameters)"
		response = self.post_json( reverse("m_offer_restart"), {
								'offer_id': response['offer_id'],
								'title':'$10 off on entree',
								'description': 'Come taste some great greek food next 30 minutes',
								'now': True,
								'duartion': 50,
								'units': 1,
								'amount': 10 }, comment)

		comment = "Redeem an offer and show total dollar spent"
		response = self.post_json( reverse("m_offer_redeem"), {
								'code': 'YZ8HY',
								'amount': 38.05 }, comment)

		comment = "Show list of past offers and details"
		response = self.get_json( reverse("m_offers_past"), {}, comment)

		comment = "Show a summary for the merchants"
		response = self.get_json( reverse("m_merchant_summary"), {}, comment)

		comment = "Show a summary visualization for the merchants"
		response = self.get_json( reverse("m_merchant_summary_viz"), {}, comment)

		comment = "Start a new point based offer (units=2), point based offer durations are by days"
		response = self.get_json( reverse("m_point_offer_start"), {
								'title':'$10 off on pants',
								'description': 'Come get some new pair of pants',
								'now': False,
								'date': '2011-05-18',
								'time': '06:00:00 PM',
								'units': 2,
								'days': 7,
								'amount': 1000 }, comment)


		offer_id = response["offer_id"]


		comment = "Show active point offers" 
		response = self.get_json( reverse("m_point_offers_active"), {}, comment)

		comment = "Show past point offers" 
		response = self.get_json( reverse("m_point_offers_past"), {}, comment)

		comment = "Start a point offer" 
		response = self.get_json( reverse("m_point_offer_start"), {}, comment)

		comment = "Restart an existing point offer" 
		response = self.get_json( reverse("m_point_offer_restart"), {}, comment)

		comment = "Expire a point offer earlier than expiration" 
		response = self.get_json( reverse("m_point_offer_expire", args=[offer_id]), {}, comment)

		comment = "Merchant logout"
		response = self.get_json( reverse("m_logout"), {}, comment)
	
		email = "user2@merchant.com"
		password = "hello"

		comment = "Merchant registration"
		response = self.post_json( reverse("m_register_merchant"), {'business': "Costumes from Mars", 'phone': '917-242-4243', 'email': email, 'password': password, 'zipcode': '02139'}, comment)

		comment = "Merchant logout"
		response = self.get_json( reverse("m_logout"), {}, comment, redirect=True)
	
	
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

