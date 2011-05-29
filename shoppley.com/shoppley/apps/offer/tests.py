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
from django.core.management.base import NoArgsCommand,CommandError
import json 
from mailer.models import Message
from django.contrib.auth.models import *
from datetime import datetime, timedelta
from django.conf import settings
from offer.management.commands.check_sms import Command 

from shoppleyuser.models import *
from offer.models import OfferCode, Offer, ForwardState, Feature, OfferCodeAbnormal, TrackingCode
from shoppleyuser.utils import parse_phone_number
from pyparsing import *
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

	def create_customers(self):
		customers=[["c1@mit.edu","12345", "0000000001"],
								["c2@mit.edu","12345", "0000000002"],
								["c3@mit.edu","12345", "0000000003"],
								["c4@mit.edu","12345", "0000000004"],]
		for o in customers:
			u,created= User.objects.get_or_create(username=o[0],email=o[0],password=o[1])
			u.is_active=True
			u.save()
			cambridge = ZipCode.objects.get(code="02139")
			c, created= Customer.objects.get_or_create(user=u,address_1="",address_2="", zipcode=cambridge,phone=o[2])

	def create_offers(self):

		offer_reader = [["617-000-0001", "Kwan's Pizza1","$5 off everything in our menu","kool1@mit.edu",5,10,10,"00001",],
				["617-000-0002", "Kwan's Pizza2","$10 off everything in our menu","kool2@mit.edu",10,5,30, "00002"],
				["617-000-0003", "Kwan's Pizza3","$15 off everything in our menu","kool3@mit.edu",15,20,5, "00003"],
				]

		i =0
		for row in offer_reader:
			m_phone = parse_phone_number(row[0])
			name = row[1]
			description = row[2]
			time_stamp = datetime.now()
			dollar_off = row[4]
			duration = row[5]
			customers = row[6]
			code = row[7]
			u, created = User.objects.get_or_create(username=row[3], email=row[3])
			u.set_password("hello")
			u.is_active=True
			u.save()
			cambridge = ZipCode.objects.get(code="02139")

			m, created = Merchant.objects.get_or_create(phone = m_phone, defaults={'user':u, 'address_1':"15 Pearl St.",'zipcode':cambridge, 'balance':100, 'business_name':"Kwan's Pizza", 'admin':"Kwan"})
			if created:
				print "Cant find Kwan's pizza"
			
			o, created = Offer.objects.get_or_create(merchant=m,name=name,description=description, defaults={'dollar_off':dollar_off, 'time_stamp':time_stamp,'starting_time':time_stamp,'duration':duration,'max_offers':customers})
			c = Customer.objects.all()[0]
			
			oc, created = OfferCode.objects.get_or_create(code=code,
																										offer=o, 
																										customer=c, 
																										time_stamp=datetime.now(), 
																										expiration_time=datetime.now() + timedelta(minutes=o.duration))
		

	def create_merchants(self):

		zip_reader = [
					["US", "02139", "Cambridge", "Massachusetts", "MA", "kool1@mit.edu", "Kwan's Pizza1", "", "", "-42.23432", "42.23432", "617-000-0001"],
					["US", "02142", "Boston", "Massachusetts", "MA", "", "kool2@mit.edu", "Kwan's Pizza2", "", "-42.23432", "42.23432" ,"617-000-0002"],
					["US", "02138", "Somerville", "Massachusetts", "MA", "kool3@mit.edu", "Kwan's Pizza3", "", "", "-42.23432", "42.23432","617-000-0003"]]

		for row in zip_reader:
			country_obj, created = Country.objects.get_or_create(name="United States", code=row[0])			
			phone = parse_phone_number(row[11])
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

			u, created = User.objects.get_or_create(username=row[5], email=row[5])
			u.set_password("hello")
			u.is_active=True
			u.save()

			cambridge = ZipCode.objects.get(code="02139")
			m, created = Merchant.objects.get_or_create(user=u, address_1="15 Pearl St.",zipcode=cambridge, phone=phone, balance=100, business_name=row[6], admin="Kwan")
						

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

		self.create_customers()
		fixture = AutoFixture(Feature)
		features = fixture.create(10)

		fixture = AutoFixture(Offer)
		offers = fixture.create(10)
		for o in offers:
			fixture = AutoFixture(OfferCode)
			codes = fixture.create(10)
		self.create_offers()

	def post_json(self, command, params={}, comment="No comment"):
		print "*************************************************"
		print comment
		print "-------------------------------------------------"
		print "POST URL:", command
		print "PARAMS:", self.pp.pprint(params) 
		response = self.client.post(command, params)
		#print response
		print "-------------------------------------------------"
		print "RESPONSE:"
		if response.status_code == 302:
			print "Shouldn't be redirecting to: %s"%response["Location"]
		self.assertEqual(response.status_code, 200)
		print json.dumps(json.loads(response.content), indent=2)
		return json.loads(response.content)

	def get_json(self, command, params={}, comment="No comment"):
		print "*************************************************"
		print comment
		print "-------------------------------------------------"
		print "GET URL:", command
		print "PARAMS:", self.pp.pprint(params)
		response = self.client.get(command, params)
		#print response
		print "-------------------------------------------------"
		print "RESPONSE:"
		if response.status_code == 302:
			print "Shouldn't be redirecting to: %s"%response["Location"]
		self.assertEqual(response.status_code, 200)
		print json.dumps(json.loads(response.content), indent=2)
		return json.loads(response.content)

	def get_web(self, command, params={}, comment="No comment"):
		print "*************************************************"
		print comment
		print "-------------------------------------------------"
		print "GET WEB URL", command
		print "PARAMS:", self.pp.pprint(params)
		response = self.client.get(command, params)
		return response

	def post_web(self, command, params={}, comment="No comment"):
		print "*************************************************"
		print comment
		print "-------------------------------------------------"
		print "POST WEB URL", command
		print "PARAMS:", self.pp.pprint(params)
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
		
	def test_txt_messages(self):
		cmd = Command()
		cmd.DEBUG = True
		self.failIfEqual(cmd.DEBUG,False)
		msg1= {"from":"8043329436", "text":"signup smengl@mit.edu 02139"}
		pattern = Word(alphas+"_") + ZeroOrMore(Word(alphanums+"!@#$%^&*()_+=-`~,./<>?:;\'\"{}[]\\|"))
		eles=pattern.parseString(msg1["text"])
		self.failUnlessEqual(len(eles),3)
		self.failUnlessEqual(eles[0],"signup")
		self.failUnlessEqual(eles[1],"smengl@mit.edu")
		self.failUnlessEqual(eles[2],"02139")


		msg2={"from":"8043329436", "text":"merchant_signup m1@mit.edu 02139 m1"}
		cmd.test_handle(msg2)
		cambridge=ZipCode.objects.get(code="02139")
		
		m= Merchant.objects.filter(zipcode=cambridge,business_name="m1")

		self.failUnlessEqual(m.count(),1)
		print m[0].user.password, m[0].user.username
		#count=0
		#for i in OfferCode.objects.all():
		#	print str(count), i
		#	count = count+1

		print "************* TEST 1 ***************"
		msg2={"from":"6170000001", "text":"offer Pizza free all day"}
		self.failUnlessEqual(Offer.objects.filter(description="Pizza free all day").count(),0)
		cmd.test_handle(msg2)
		offer =Offer.objects.filter(description="Pizza free all day")
		self.failUnlessEqual(offer.count(),1)
		offer = offer[0]
		merchant = Merchant.objects.get(phone="6170000001")
		self.failUnlessEqual(offer.merchant, merchant)
		track = TrackingCode.objects.get(offer = offer).code
		print track
		print "************* TEST 2: INFO ***************"
		msg3={"from":"0000000001", "text":"info 00001 00002 00003"}
		cmd.test_handle(msg3)
		msg4={"from":"0000000001", "text":"info 00004"}
		error = False
		try:
			cmd.test_handle(msg4)
		except CommandError:
			error = True
		self.assertTrue(error)

		print "************* TEST 3: STOP ***************"
		msg5={"from":"0000000001", "text": "stop offer"}
		cmd.test_handle(msg5)
		c=Customer.objects.filter(phone__iexact=msg5["from"])
		self.failUnlessEqual(c.count(), 1)
		self.failUnlessEqual(c[0].active, False)
		print "************* TEST 4: START ***************"
		msg6={"from":"0000000001", "text": "start offer"}
		cmd.test_handle(msg6)
		self.failUnlessEqual(c[0].active, True)

		print "************* TEST 5: FORWARD ***************"
		msg7={"from":"0000000001", "text": "forward 00002 000000002"}
		cmd.test_handle(msg7)
		forwarder = Customer.objects.filter(phone__iexact="0000000001")
		self.failUnlessEqual(forwarder.count(),1)
		forwarder = forwarder[0]
		
		receiver = Customer.objects.filter(phone__iexact="0000000002")
		self.failUnlessEqual(receiver.count(),1)
		receiver = receiver[0]

		oc_ori = OfferCode.objects.filter(code = "00002")
		self.failUnlessEqual(oc_ori.count(),1)
		
		oc = OfferCode.objects.filter(offer__id=oc_ori[0].offer.id,customer__id=receiver.id)
		self.failUnlessEqual(oc.count(),1)
		oc = oc[0]
		self.failUnlessEqual(oc.forwarder.id,forwarder.id)
		print "ori_code: %s" % oc_ori[0].code, "code: %s " % oc.code
		self.failIfEqual(oc.code,oc_ori[0].code)
		print "************* TEST 5a: FORWARD TO NON-CUSTOMER***************"

		msg7a={"from":"0000000001", "text": "forward 00002 000000010"}
		cmd.test_handle(msg7a)
		forwarder = Customer.objects.filter(phone__iexact="0000000001")
		self.failUnlessEqual(forwarder.count(),1)
		forwarder = forwarder[0]
		
		rec_user = User.objects.filter(username__iexact="000000010")
		self.failUnlessEqual(rec_user.count(),1)
		print rec_user[0].email
		self.failUnlessEqual(rec_user[0].email,"")
		receiver = Customer.objects.filter(phone__iexact="000000010")
		self.failUnlessEqual(receiver.count(),1)
		receiver = receiver[0]

		oc2 = OfferCode.objects.filter(offer__id=oc_ori[0].offer.id,phone__iexact="000000010")
		self.failUnlessEqual(oc2.count(),1)
		oc2 = oc2[0]
		self.failUnlessEqual(oc2.forwarder.id,forwarder.id)
		self.failUnlessEqual(oc2.customer.id,receiver.id)
		print "ori_code: %s" % oc_ori[0].code, "code: %s " % oc2.code
		self.failIfEqual(oc2.code,oc_ori[0].code)
		self.failIfEqual(oc2.code,oc.code)
		print "************* TEST 5b: FORWARD REACH LIMIT***************"

		msg7b={"from":"0000000001", "text": "forward 00002 000000010"}
		cmd.test_handle(msg7b)

		print "************* TEST 5c: FORWARD A CODE THE CUSTOMER DOES NOT OWN***************"
		# forward code not the customer's
		msg7c={"from":"0000000002", "text": "forward 00002 000000010"}
		offercode = OfferCode.objects.get(code = "00002")
		customer = Customer.objects.get(phone__iexact="0000000002")
		self.failIfEqual(offercode.customer, customer)
		f_state = ForwardState.objects.filter(customer=customer,offer=offercode.offer)
		error = False		
		try:
			cmd.test_handle(msg7c)
		except CommandError:
			error = True
		self.assertTrue(error)
		# forward code that does not exist
		print "************* TEST 5d: FORWARD A CODE THAT DOES NOT EXIST***************"
		msg7d={"from":"0000000002", "text": "forward 0000X 000000010"}
		error = False
		try:
			cmd.test_handle(msg7d)
		except CommandError:
			error = True
		self.assertTrue(error)
		# forward to someone who already has the offer
		print "************* TEST 5e: FORWARD TO SOMEONE WHO ALREADY HAS THE OFFER***************"
		msg7e={"from":"0000000002", "text": "forward 00001 000000010"}
		error = False
		try:
			cmd.test_handle(msg7e)
		except CommandError:
			error= True
		self.assertTrue(error)
		
		print "************* TEST 6: REDEEM ***************"
		msg8={"from":"6170000001", "text": "redeem 00001 0000000001"}
		customer = Customer.objects.filter(phone__iexact="0000000001")
		self.failUnlessEqual(customer.count(),1)
		customer = customer[0]
		oc = OfferCode.objects.filter(code__iexact="00001")
		self.failUnlessEqual(oc.count(),1)
		oc = oc[0]

		cmd.test_handle(msg8)
		self.failIfEqual(oc.redeem_time,"")
		print "************* TEST 6a: REDEEM MERCHANT IS NOT THE OWNER OF THE OFFER***************"
		# merchant is not the owner of the offer
		msg8a={"from":"6170000001", "text": "redeem 00002 0000000001"}
		customer = Customer.objects.filter(phone__iexact="0000000001")
		self.failUnlessEqual(customer.count(),1)
		customer = customer[0]
		oc = OfferCode.objects.filter(code__iexact="00002")
		self.failUnlessEqual(oc.count(),1)
		oc = oc[0]
		error = False
		try:
			cmd.test_handle(msg8a)
		except CommandError:
			error = True
		self.assertTrue(error)
		self.failIfEqual(oc.redeem_time,"")

		print "************* TEST 6b: REDEEM NON-EXISTENT CODE***************"
		# redeem code that does not exist
		msg8b={"from":"6170000001", "text": "redeem 0000X 0000000001"}
		error=False
		try:
			cmd.test_handle(msg8b)
		except CommandError:
			error= True
		self.assertTrue(error)


		print "************* TEST 6d: REDEEM CODE REUSE**************"
		msg8d={"from":"6170000001", "text": "redeem 00001 0000000001"}
		error = False		
		try:
			cmd.test_handle(msg8)
		except:
			error = True
		self.assertTrue(error)

		print "************* TEST 6c: REDEEMER != CODE'S CUSTOMER***************"
		offer = OfferCode.objects.get(code="00002").offer
		customer2 = Customer.objects.get(phone="0000000002")
		OfferCode(offer=offer,code="000X2",customer=customer2,phone="0000000002",time_stamp=datetime.now(),expiration_time=datetime.now() + timedelta(minutes=offer.duration)).save()
		# redeemer and code's owner are different
		msg8c={"from":"6170000002", "text": "redeem 000X2 0000000001"}
		error = False
		try:
			cmd.test_handle(msg8c)
		except CommandError:
			error = True
		self.assertTrue(error)

		print "************* TEST 7: SIGNUP ***************"
		msg9={"from":"0000000010", "text": "signup s10@mit.edu 02139"}
		self.failUnlessEqual(Customer.objects.filter(phone__iexact=msg9["from"]).count(),0)
		cmd.test_handle(msg9)
		newc=Customer.objects.filter(phone__iexact=msg9["from"])
		self.failUnlessEqual(newc.count(),1)
		self.failUnlessEqual(newc[0].user.email , "s10@mit.edu")
		self.failUnlessEqual(newc[0].phone , "0000000010")

		print "************* TEST 7a: RESIGNUP ***************"
		msg9a={"from":"0000000010", "text": "signup s10@mit.edu 02139"}
		error = False
		self.failUnlessEqual(Customer.objects.filter(phone__iexact=msg9a["from"]).count(),1)
		cmd.test_handle(msg9a)
		self.failUnlessEqual(Customer.objects.filter(phone__iexact=msg9a["from"]).count(),1)


		print "************* TEST 7b: SIGNUP: reuse EMAIL ***************"
		msg9b={"from":"0000000011", "text": "signup s10@mit.edu 02139"}
		error = False
		try:
			cmd.test_handle(msg9b)
		except CommandError:
			error = True
		self.assertTrue(error)

		print "************* TEST 7c: SIGNUP: reuse PHONE ***************"
		msg9c={"from":"0000000010", "text": "signup s11@mit.edu 02139"}
		self.failUnlessEqual(Customer.objects.filter(phone__iexact=msg9c["from"]).count(),1)
		cmd.test_handle(msg9c)
		self.failUnlessEqual(Customer.objects.filter(phone__iexact=msg9c["from"]).count(),1)

		print "************* TEST 8: MERCHANT_SIGNUP ***************"
		msg10={"from":"0000000020", "text": "merchant_signup m20@mit.edu 02139 test Merchant name"} # what if merchant business name contains many words
		cmd.test_handle(msg10)
		tokens = pattern.parseString(msg10["text"])
		newu=User.objects.filter(email=tokens[1], username=tokens[1])
		self.failUnlessEqual(newu.count(),1)
		newm=Merchant.objects.filter(phone__iexact=msg10["from"])
		self.failUnlessEqual(newm.count(),1)
		self.failUnlessEqual(newm[0].business_name,"test Merchant name")

		print "************* TEST 8a: RESIGNUP ***************"
		msg10a={"from":"0000000020", "text": "merchant_signup m20@mit.edu 02139 test Merchant name"}
		error = False
		self.failUnlessEqual(Merchant.objects.filter(phone__iexact=msg10a["from"]).count(),1)
		cmd.test_handle(msg10a)
		self.failUnlessEqual(Merchant.objects.filter(phone__iexact=msg10a["from"]).count(),1)


		print "************* TEST 8b: SIGNUP: reuse EMAIL ***************"
		msg10b={"from":"0000000021", "text": "merchant_signup m20@mit.edu 02139 test Merchant name"}
		error = False
		try:
			cmd.test_handle(msg10b)
		except CommandError:
			error = True
		self.assertTrue(error)

		print "************* TEST 8c: SIGNUP: reuse PHONE ***************"
		msg10c={"from":"0000000020", "text": "merchant_signup m21@mit.edu 02139 test Merchant name"}
		self.failUnlessEqual(Merchant.objects.filter(phone__iexact=msg10c["from"]).count(),1)
		cmd.test_handle(msg10c)
		self.failUnlessEqual(Merchant.objects.filter(phone__iexact=msg10c["from"]).count(),1)

		print "************* TEST 9: STATUS ***************"
		# test phone number isnt in record, and text for info
		msg11={"from":"6170000001", "text":"status %s" % track}
		cmd.test_handle(msg11)
		offercode= OfferCode.objects.get(customer=Customer.objects.get(phone="0000000001"),offer=TrackingCode.objects.get(code=track).offer)

		msg11a = {"from":"0000000001", "text":"forward %s 0000000010" % offercode.code}
		cmd.test_handle(msg11a)


		msg11b={"from":"6170000001", "text":"status %s" % track}
		cmd.test_handle(msg11b)


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

