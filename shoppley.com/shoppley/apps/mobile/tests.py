"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings

import csv, json
import pprint
import sqlite3, random
import time
from datetime import datetime, timedelta

from shoppleyuser.utils import parse_phone_number
from shoppleyuser.models import ShoppleyUser, Country, Region, City, ZipCode, Merchant, Customer, Category, ShoppleyPhone, CustomerPhone, MerchantPhone
from offer.models import Offer, OfferCode, BlackListWord


from offer.management.commands import distribute 

API_VERSION = 1;

class SimpleTest(TestCase):

	def runTest(self):
		pass

	def setUp(self):
		self.pp = pprint.PrettyPrinter(indent=2)
		self.f = open("/tmp/shoppley.test.out.txt", "w")

		us, created = Country.objects.get_or_create(name="United States", code="US")
		region, created = Region.objects.get_or_create(name="Hawaii", code="HI", country=us)
		city, created = City.objects.get_or_create(name="Aiea", region=region)
		zipcode1, created = ZipCode.objects.get_or_create(code="96701", city=city)
		city, created = City.objects.get_or_create(name="Anahola", region=region)
		zipcode2, created = ZipCode.objects.get_or_create(code="96703", city=city)
		city, created = City.objects.get_or_create(name="Ahualoa", region=region)
		zipcode3, created = ZipCode.objects.get_or_create(code="96727", city=city)

		# create users
		u, created = User.objects.get_or_create(username="user1@customer.com")
		u.email="user1@customer.com"
		u.set_password("hello")
		u.save()
		
		num = parse_phone_number("6176829602")
		if not Customer.objects.filter(user=u).exists():
			c, created = Customer.objects.get_or_create(user=u, address_1="", address_2="", zipcode=zipcode1, balance=1000)
			p, pcreated = CustomerPhone.objects.get_or_create(customer = c, number = num)
			c.active = True
			c.verified = True
			c.save()
			c.set_location_from_address()
		
		u, created = User.objects.get_or_create(username="user2@customer.com")
		u.email="user2@customer.com"
		u.set_password("hello")
		u.save()
		
		num = parse_phone_number("6174538710")
		if not Customer.objects.filter(user=u).exists():
			c, created = Customer.objects.get_or_create(user=u, address_1="15 Franklin St.", address_2="", zipcode=zipcode1, balance=1000)
			p, pcreated = CustomerPhone.objects.get_or_create(customer = c, number = num)
			c.active = True
			c.verified = True
			c.save()
			c.set_location_from_address()

		u, created = User.objects.get_or_create(username="user3@customer.com")
		u.email="user3@customer.com"
		u.set_password("hello")
		u.save()
		
		#617-682-9784 Meng's other googlevoice
		num = parse_phone_number("6176829784")
		if not Customer.objects.filter(user=u).exists():
			c, created = Customer.objects.get_or_create(user=u, address_1="15 Franklin St.", address_2="", zipcode=zipcode2,balance=1000)
			p, pcreated = CustomerPhone.objects.get_or_create(customer = c, number = num)
			c.active = True
			c.verified = True
			c.save()
			c.set_location_from_address()

		u, created = User.objects.get_or_create(username="user1@merchant.com")
		u.email="user1@merchant.com"
		u.set_password("hello")
		u.save()
		
		#617-453-8665 Meng's googlevoice number
		num = parse_phone_number("6174538665")
		if not Merchant.objects.filter(user=u).exists():
			m, created = Merchant.objects.get_or_create(user=u, address_1="", address_2="", zipcode=zipcode1, phone=num, balance=10000, business_name="Jane's Shoe Store", admin="Jane Sullivan", url="http://www.shoppley.com")
			p, pcreated =MerchantPhone.objects.get_or_create(merchant = m, number = num)
			m.active = True
			m.verified = True
			m.save()
			m.set_location_from_address()
			print "Merchant location set:", m.location

		u, created = User.objects.get_or_create(username="user2@merchant.com")
		u.email="user2@merchant.com"
		u.set_password("hello")
		u.save()

		num = parse_phone_number("6178710710")
		if not Merchant.objects.filter(user=u).exists():
			m, created = Merchant.objects.get_or_create(user=u, address_1="190 Mass Av.", address_2="", zipcode=zipcode1, phone=num, balance=10000, business_name="Flour Bakery", admin="Kevin Bacon", url="http://www.shoppley.com")
			p, pcreated =MerchantPhone.objects.get_or_create(merchant = m, number = num)
			m.active = True
			m.verified = True
			m.save()
			m.set_location_from_address()

		u, created = User.objects.get_or_create(username="user3@merchant.com")
		u.email="user3@merchant.com"
		u.set_password("hello")
		u.save()

		num = parse_phone_number("6177154416")
		if not Merchant.objects.filter(user=u).exists():
			m, created = Merchant.objects.get_or_create(user=u, address_1="190 Mass Av.", address_2="", zipcode=zipcode2, phone=num, balance=10000, business_name="John's Auto", admin="John Jacobson", url="http://www.shoppley.com")
			p, pcreated =MerchantPhone.objects.get_or_create(merchant = m, number = num)
			m.active = True
			m.verified = True
			m.save()
			m.set_location_from_address()



		shop_user = Customer.objects.get(user__email="user1@customer.com")
		shop_merch = Merchant.objects.get(user__email="user1@merchant.com")
		shop_user.merchant_likes.add(shop_merch)

		# create categories
		categories = [("Dining & Nightlife", "dining"), ("Health & Beauty", "health"), ("Fitness","fitness"), ("Retail & Services", "retail"), ("Activities & Events", "activities"), ("Special Interests", "special")]
		for cat in categories:
			category, created = Category.objects.get_or_create(name=cat[0], tag=cat[1])


		self.distributor = distribute.Command()


	
	def iphone_review(self):

		us, created = Country.objects.get_or_create(name="United States", code="US")
		region, created = Region.objects.get_or_create(name="Hawaii", code="HI", country=us)
		city, created = City.objects.get_or_create(name="Huna", region=region)
		zipcode1, created = ZipCode.objects.get_or_create(code="96727", city=city)

		# create users
		u, created = User.objects.get_or_create(username="user1@customer.com")
		u.email="user1@customer.com"
		u.set_password("hello")
		u.save()
		
		num = parse_phone_number("6176829602")
		if not Customer.objects.filter(user=u).exists():
			c, created = Customer.objects.get_or_create(user=u, address_1="", address_2="", zipcode=zipcode1, balance=1000)
			p, pcreated = CustomerPhone.objects.get_or_create(customer = c, number = num)
			c.active = True
			c.verified = True
			c.save()
			c.set_location_from_address()
	
		u, created = User.objects.get_or_create(username="user1@merchant.com")
		u.email="user1@merchant.com"
		u.set_password("hello")
		u.save()
		
		#617-453-8665 Meng's googlevoice number
		num = parse_phone_number("6174538665")
		if not Merchant.objects.filter(user=u).exists():
			m, created = Merchant.objects.get_or_create(user=u, address_1="", address_2="", zipcode=zipcode1, phone=num, balance=10000, business_name="Dunkin Donuts", admin="Jake Sullivan", url="http://www.shoppley.com")
			p, pcreated =MerchantPhone.objects.get_or_create(merchant = m, number = num)
			m.active = True
			m.verified = True
			m.save()
			m.set_location_from_address()

		shop_user = Customer.objects.get(user__email="user1@customer.com")
		shop_merch = Merchant.objects.get(user__email="user1@merchant.com")
		shop_user.merchant_likes.add(shop_merch)

		offers = ["$5 off shoes brands, Nike, Reebok",
				"10% off Abercrombie flip flops",
								"Save $15 on your purchase of dress shoes",
								"Buy dress shoes today & get free socks"]

		m = Merchant.objects.get(user__email="user1@merchant.com")	
		for o in offers:
			# start offers 30 minutes ago
			input_time = datetime.now()-timedelta(minutes=30)
			offer = Offer(merchant=m, title=o[:40], description=o, time_stamp=input_time, duration=40320, starting_time=input_time) 
			offer.save()

		self.distributor.handle_noargs()

	def post_json(self, command, params={}, comment="No comment", redirect=False, shouldPrint=True):
		params["v"] = API_VERSION
		output = []
		output.append("*"*100+"\n")
		output.append(comment+"\n")
		output.append("-"*100+"\n")
		output.append("POST URL: %s\n"%command)
		output.append("PARAMS:\n")
		output.append(self.pp.pformat(params)+"\n")
		response = self.client.post(command, params)
		#print response
		output.append("-"*100+"\n")
		output.append("RESPONSE:\n")
		if redirect:
			if response.status_code == 302:
				output.append("Should be redirecting to: %s"%response["Location"]+"\n")
				return "Redirect to:",response["Location"]
			else:
				return "Response code:", response.status_code
		else:
			self.assertEqual(response.status_code, 200)
		output.append(json.dumps(json.loads(response.content), indent=2)+"\n")
		if shouldPrint:
			self.f.writelines(output)
		return json.loads(response.content)

	def get_json(self, command, params={}, comment="No comment", redirect=False, shouldPrint=True):
		params["v"] = API_VERSION
		
		output = []
		output.append("*"*100+"\n")
		output.append(comment+"\n")
		output.append("-"*100+"\n")
		output.append("GET URL: %s\n"%command)
		output.append("PARAMS:\n")
		output.append(self.pp.pformat(params)+"\n")
		response = self.client.get(command, params)
		#print response
		output.append("-"*100+"\n")
		output.append("RESPONSE:\n")
		if redirect:
			if response.status_code == 302:
				output.append("Should be redirecting to: %s"%response["Location"]+"\n")
				return "Redirect to:",response["Location"]
			else:
				return "Response code:", response.status_code
		else:
			self.assertEqual(response.status_code, 200)
		output.append(json.dumps(json.loads(response.content), indent=2)+"\n")
		if shouldPrint:
			self.f.writelines(output)
		return json.loads(response.content)

	def get_web(self, command, params={}, comment="No comment", shouldPrint=True):
		output = []
		output.append("*"*100+"\n")
		output.append(comment+"\n")
		output.append("-"*100+"\n")
		output.append("GET WEB URL: %s\n"%command)
		output.append("PARAMS:\n")
		output.append(self.pp.pformat(params)+"\n")
		response = self.client.get(command, params)
		if shouldPrint:
			self.f.writelines(output)
		return response

	def post_web(self, command, params={}, comment="No comment", shouldPrint=True):
		output = []
		output.append("*"*100+"\n")
		output.append(comment+"\n")
		output.append("-"*100+"\n")
		output.append("POST WEB URL: %s\n"%command)
		output.append("PARAMS:\n")
		output.append(self.pp.pformat(params)+"\n")
		response = self.client.post(command, params)
		if shouldPrint:
			self.f.writelines(output)
		return response

	def create_test_offers(self):
		"""
			Generate several offers by multiple merchants that targets two different users in two different
			zip codes
		"""
	
		offers = ["$5 off shoes brands, Nike, Reebok",
				"10% off Abercrombie flip flops",
								"Save $15 on your purchase of dress shoes",
								"Buy dress shoes today & get free socks"]

		m = Merchant.objects.get(user__email="user1@merchant.com")	
		for o in offers:
			# start offers 30 minutes ago
			input_time = datetime.now()-timedelta(minutes=30)
			offer = Offer(merchant=m, title=o[:40], description=o, time_stamp=input_time, duration=40320, starting_time=input_time) 
			offer.save()
			#print offer.distribute()
			

		if not settings.SMS_DEBUG:
			self.assertGreaterEqual(offer.offercode_set.all().count(), 0)

		offers = ["$1 off Chicken Sandwiches",
				"Free drink when you order $10 or more",
								"Half priced cookies"]

		m = Merchant.objects.get(user__email="user2@merchant.com")	
		for o in offers:
			# start offers 30 minutes ago
			input_time = datetime.now()-timedelta(minutes=30)
			offer = Offer(merchant=m, title=o[:40], description=o, time_stamp=input_time, duration=40320, starting_time=input_time) 
			offer.save()
			#offer.distribute()

		if not settings.SMS_DEBUG:
			self.assertGreaterEqual(offer.offercode_set.all().count(), 0)

		offers = ["$1 off Oil Change",
						"20% off car wash",
						"$30 snow tire exchange"]

		m = Merchant.objects.get(user__email="user3@merchant.com")	
		for o in offers:
			# start offers 30 minutes ago
			input_time = datetime.now()-timedelta(minutes=30)
			offer = Offer(merchant=m, title=o[:40], description=o, time_stamp=input_time, duration=40320, starting_time=input_time) 
			offer.save()
			#offer.distribute()

		self.distributor.handle_noargs()
    
		self.redeem_offer()

		if not settings.SMS_DEBUG:
			self.assertGreaterEqual(offer.offercode_set.all().count(), 0)

	def create_spam_offers(self):
		"""
			Generate several offers by multiple merchants that targets two different users in two different
			zip codes
		"""
	
		offers = ["$5 off shit ass brands, Nike, Reebok",
				"10% off American Eagle flip flops",
								"Save $15 on your mother f** of dress shoes",
								"Buy dress dope pal & get free socks"]

		m = Merchant.objects.get(user__email="user1@merchant.com")	
		for o in offers:
			# start offers 30 minutes ago
			input_time = datetime.now()-timedelta(minutes=30)
			offer = Offer(merchant=m, title=o[:40], description=o, time_stamp=input_time, duration=40320, starting_time=input_time) 
			offer.save()
			#print offer.distribute()
			

		if not settings.SMS_DEBUG:
			self.assertGreaterEqual(offer.offercode_set.all().count(), 0)

		offers = ["$1 off Chicken Fart",
				"Free orange juice when you order $10 or more",
								"Half priced cum cookies"]

		m = Merchant.objects.get(user__email="user2@merchant.com")	
		for o in offers:
			# start offers 30 minutes ago
			input_time = datetime.now()-timedelta(minutes=30)
			offer = Offer(merchant=m, title=o[:40], description=o, time_stamp=input_time, duration=40320, starting_time=input_time) 
			offer.save()
			#offer.distribute()

		if not settings.SMS_DEBUG:
			self.assertGreaterEqual(offer.offercode_set.all().count(), 0)

		offers = ["$1 off Wet Oil Change",
						"20% off car ass",
						"$30 Summer tire exchange"]

		m = Merchant.objects.get(user__email="user3@merchant.com")	
		for o in offers:
			# start offers 30 minutes ago
			input_time = datetime.now()-timedelta(minutes=30)
			offer = Offer(merchant=m, title=o[:40], description=o, time_stamp=input_time, duration=40320, starting_time=input_time) 
			offer.save()
			#offer.distribute()

		self.distributor.handle_noargs()

		if not settings.SMS_DEBUG:
			self.assertGreaterEqual(offer.offercode_set.all().count(), 0)

	def create_blacklist_words(self):
		bl_words = ['fuck', 'f**', 'f*', 'f***', 'f**k', 'shit', 'ass', 'cum', 'dope', 'shit', 's**t', 's*t', 'fart']
		for w in bl_words:
			word, created = BlackListWord.objects.get_or_create(word=w)

	def redeem_offer(self):
		"""
			Redeems an offer of user1@customer.com 
		"""

		u = User.objects.get(email="user1@customer.com")
		c = u.shoppleyuser.customer
		o = random.sample( OfferCode.objects.filter(customer=c), 2 )
		o[0].redeem()
		o[1].redeem()

	def random_offer(self):

		u = User.objects.get(email="user1@customer.com")
		c = u.shoppleyuser.customer
		
		while o.redeem_time != None:
			o = random.sample( OfferCode.objects.filter(customer=c), 1 )

		return o

	def expire_offer(self, email):
		u = User.objects.get(email=email)
		m = u.shoppleyuser.merchant
		
		#expired_offers = Offer.objects.filter(merchant=m, expired=True)
		expired_offers = Offer.objects.filter(merchant=m, expired_time__lt=datetime.now())

		if expired_offers.exists():
		
			return random.sample( expired_offers, 1 )[0]
		
		#valid_offers =  Offer.objects.filter(merchant=m, expired=False)
		valid_offers= Offer.objects.filter(merchant=m, expired_time__gt=datetime.now(), is_processing=False)
		if valid_offers.exists():
			o = random.sample(valid_offers, 1)[0]
			o.expire(True)
			# expire all offer codes
			for c in o.offercode_set.all():
				c.expiration_time = datetime.now()
				c.save()

			return o
		else:
			return None

	def get_offer_code(self, email):
		u = User.objects.get(email=email)
		m = u.shoppleyuser.merchant
		
		offers = Offer.objects.filter(merchant=m, expired_time__gt=datetime.now(), is_processing=False)
		codes = []	
		for o in offers:
			for c in o.offercode_set.all():
				codes.append(c)

		return random.sample(codes, 1)[0]


	def test_mobile_api(self):
		"""
			Generate mobile API doc as it tests
		"""

		self.f = open(settings.PROJECT_ROOT+"/media/mobile.api.txt", "w")	

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
		response = self.post_json( reverse("m_offers_current"), {'lat':21.38583, 'lon':-157.93083}, comment)
		# for 96701 21.3858333000000016 -157.9308332999999891 

		print "Num offers: %d" % len(response["offers"])

		offer_to_request_code = None
		for o in response["offers"]:
			if not "code" in o:
				offer_to_request_code = o["offer_id"]
				break

		self.assertTrue(offer_to_request_code is not None);
		comment = "Request offercode for offer."
		response = self.post_json( reverse("m_offer_offercode"), {"offer_id": offer_to_request_code}, comment)
				
		offer_code_to_forward = response["offer"]["code"]

		comment = "Show redeemed offers, it also returns offer details"
		response = self.get_json( reverse("m_offers_redeemed"), {}, comment)

		self.assertTrue(len(response["offers"]) > 0);
		review_offer_id = response["offers"][0]["offer_code_id"]

		comment = "Forward offer to a list of phone numbers (text messages are sent to them and new accounts created if they are not current users with text message showing random passwords)"
		response = self.post_json( reverse("m_offer_forward"), {'offer_code': offer_code_to_forward,'phones':['617-877-2345', '857-678-7897', '617-871-0710', '617-453-8665'], 'note': 'This offer might interest you.'}, comment)

		comment = "Provide feedback on an offer"
		response = self.post_json( reverse("m_offer_feedback"), {'offer_code_id': review_offer_id, 'feedback':'The fish dish was amazing'}, comment)

		comment = "Rate an offer 1-5, 0 if unrated"
		response = self.post_json( reverse("m_offer_rate"), {'offer_code_id': review_offer_id, 'rating':5}, comment)
		
		comment = "Send iwant message"
		response = self.post_json( reverse("m_iwant"), {'request':'yodlor'}, comment)

		# test points
		# comment = "Shows a summary of accumulated points for customer"
		# response = self.get_json( reverse("m_customer_point_summary"), {}, comment)
		# 
		# comment = "Shows a list of point offers one can use to redeem (details too)"
		# response = self.get_json( reverse("m_customer_point_offers"), {}, comment)

		comment = "Customer logout"
		response = self.get_json( reverse("m_logout"), {}, comment)
					
		email = "user3@customer.com"
		password = "hello"

		comment = "Customer login"
		response = self.post_json( reverse("m_login"), {'email': email,
													'password': password}, comment)

		comment = "Show current offers, it also returns offer details (This one contains offer forwarded by another customer)"
		response = self.post_json( reverse("m_offers_current"), {'lat':21.38583, 'lon':-157.93083}, comment)


		comment = "Customer logout"
		response = self.get_json( reverse("m_logout"), {}, comment)
	
		email = "user4@customer.com"
		password = "hello"

		comment = "Customer registration"
		response = self.post_json( reverse("m_register_customer"), {'email': email, 'phone': '6178852347', 'zipcode': '96701', 'password':password}, comment)
	
		comment = "Customer logout"
		response = self.get_json( reverse("m_logout"), {}, comment, redirect=True)

		email = "user1@merchant.com"
		password = "hello"

		comment = "Merchant login"
		response = self.post_json( reverse("m_login"), {'email': email,
													'password': password}, comment)
	
		# comment = "Splash view for the merchant"
		# response = self.get_json( reverse("m_splash_view"), {}, comment)

		comment = "Show active offers for the merchant, returns offer details"
		response = self.get_json( reverse("m_offers_active"), {}, comment)
		# redemption is random so following condition is not satisfied all the time
		#self.assertEqual(response["offers"][0]["redeemed"], 1)
		
		comment = "Start a % off offer (units=0), duration if not specified will be next 90 minutes"
		response = self.post_json( reverse("m_offer_start"), {
								'title':'10% off on entree',
								'description': 'Come taste some great greek food next 30 minutes',
								'now': False,
								'date': '2011-05-18',
								'time': '06:00:00 PM',
								'duration': 60,
								'units': 0,
								'amount': 10 }, comment)
				
		comment = "Start a $ off offer (units=1), duration if not specified will be next 90 minutes"
		response = self.post_json( reverse("m_offer_start"), {
								'title':'$10 off on entree',
								'description': 'Come taste some great greek food next 30 minutes',
								'now': False,
								'date': '2011-05-18',
								'time': '06:00:00 PM',
								'duration': 30,
								'units': 1,
								'amount': 10 }, comment)

		comment = "Start a $ off offer (units=1), with start_unixtime"
		response = self.post_json( reverse("m_offer_start"), {
								'title':'$10 off on entree',
								'description': 'Come taste some great greek food next 30 minutes',
								'now': False,
								'start_unixtime': int(time.time()),
								'duration': 30,
								'units': 1,
								'amount': 10 }, comment)

		# TODO: remove this after we set expired_time during Offer construction
		self.distributor.handle_noargs()
		comment = "Show active offers for the merchant, returns offer details"
		response = self.get_json( reverse("m_offers_active"), {}, comment)
								
		comment = "Start a $ off offer NOW (units=1), duration if not specified will be next 90 minutes"
		response = self.post_json( reverse("m_offer_start"), {
								'title':'$10 off on entree',
								'description': 'Come taste some great greek food next 30 minutes',
								'now': True,
								'duration': 90,
								'units': 1,
								'amount': 10 }, comment)

		comment = "Send more of the same offer (URL param: offer_id)"
		response = self.get_json( reverse("m_offer_send_more", args=[response['offer']['offer_id']]), {}, comment) 

		resent_offer = Offer.objects.get(id=response["offer"]["offer_id"])
		self.assertEqual(resent_offer.redistribute_processing, True)
		self.assertEqual(response["result"], 0)
		self.distributor.handle_noargs()
		resent_offer = Offer.objects.get(id=response["offer"]["offer_id"])
		self.assertEqual(resent_offer.redistribute_processing, False)

		comment = "Result when offer cannot be sent more because already sent more (URL param: offer_id)"
		response = self.get_json( reverse("m_offer_send_more", args=[response['offer']['offer_id']]), {}, comment) 

		self.assertEqual(response["result"], -5)

		# send offer from a different latitude/longitude
		comment = "Start a % off offer (units=0), from a [specified lat/lon], duration if not specified will be next 120 minutes"
		response = self.post_json( reverse("m_offer_start"), {
								'title':'20% off on entree',
								'description': 'Late night mediterranean food, free sangria',
								'now': False,
								'date': '2011-05-18',
								'time': '10:00:00 PM',
								'duration': 120,
								'units': 0,
								'lat': 38.2322,
								'lon': -42.2342,
								'amount': 10 }, comment)
	
		# TODO: Need to expire some offers and send new offers
		exp_offer = self.expire_offer(email=email)
		self.assertNotEqual(exp_offer, None)
		exp_offer_id = exp_offer.id
			
		comment = "Restart from a previous offer (it allows change of parameters), gets parameters from the older offer, then call %s to start the offer (URL param: offer_id)"%reverse("m_offer_start")
		response = self.get_json( reverse("m_offer_restart", args=[exp_offer_id]), {}, comment)

		c = self.get_offer_code(email=email)

		comment = "Redeem an offer and show total dollar spent"
		response = self.post_json( reverse("m_offer_redeem"), {
								'code': c.code,
								'amount': 38.05 }, comment)

		comment = "Show list of past offers and details (URL param: 0)"
		response = self.get_json( reverse("m_offers_past", args=[0]), {}, comment)

		comment = "Show list of offers from past week (7 days) and details, used from the Summary view (URL param: 7)"
		response = self.get_json( reverse("m_offers_past", args=[7]), {}, comment)

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
		response = self.post_json( reverse("m_register_merchant"), {'business': "Costumes from Mars", 'phone': '917-242-4243', 'email': email, 'password': password, 'zipcode': '96701'}, comment)

		comment = "Merchant logout"
		response = self.get_json( reverse("m_logout"), {}, comment, redirect=True)

		self.f.close()
	
	def test_basic_addition(self):
		"""
		Tests that 1 + 1 always equals 2.
		"""
		self.assertEqual(1 + 1, 2)

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

