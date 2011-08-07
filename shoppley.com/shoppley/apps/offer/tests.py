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
from offer.management.commands.distribute import Command as DCommand
from django.contrib.sites.models import Site
from shoppleyuser.models import *
from offer.models import OfferCode, Offer, ForwardState, Feature, OfferCodeAbnormal, TrackingCode
from shoppleyuser.utils import parse_phone_number
from offer.utils import pretty_datetime
from worldbank.models import *
from pyparsing import *
#from django.contrib.sites.models import Site

class CustomerFixture(AutoFixture):
	class Values:

		us, created = Country.objects.get_or_create(name="United States", code="US")
		region, created = Region.objects.get_or_create(name="Massachusetts", code="MA", country=us)
		city, created = City.objects.get_or_create(name="Cambridge", region=region)
		zipcode1, created = ZipCode.objects.get_or_create(code="02139", city=city)


		cambridge = ZipCode.objects.filter(code="02139")[0]
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
			cambridge = ZipCode.objects.filter(code="02139")[0]
			
			c, created= Customer.objects.get_or_create(user=u,address_1="15 Pearl St.",address_2="", zipcode=cambridge, defaults={ "verified":True})
			CustomerPhone.objects.create(number=o[2],customer=c)
			if created:
				c.set_location_from_address()

			print "Created customer location:", c.location

	def create_geo_customers(self):
		customers=[["a1@mit.edu", "94002", "12345", "1000000000"],
#				["a2@mit.edu", "02135", "12345", "1000000001"],
#				["a3@mit.edu", "02142", "12345", "1000000002"],
				["a4@mit.edu", "10026", "12345", "1000000003"],
				["a5@mit.edu", "01101", "12345", "1000000004"],]

		m = Command()
		m.DEBUG = True
		for c in customers:
			msg = {"from": "%s" % c[3], "text": "#signup %s %s" % (c[0], c[1]) }
			#m = Command()
			m.test_handle(msg)
			u = Customer.objects.get(phone = "%s" % c[3])
			print "Customer location:", u.location
			print "X,Y of location:", u.location.location.x , u.location.location.y
			
	def create_more_customers(self): #for resent
		customers=[["c5@mit.edu","12345", "0000000005"],
								["c6@mit.edu","12345", "0000000006"],
								["c7@mit.edu","12345", "0000000007"],
								["c8@mit.edu","12345", "0000000008"],]
		for o in customers:
			u,created= User.objects.get_or_create(username=o[0],email=o[0],password=o[1])
			u.is_active=True
			u.save()
			cambridge = ZipCode.objects.filter(code="02139")[0]
			
			c, created= Customer.objects.get_or_create(user=u,address_1="",address_2="", zipcode=cambridge, defaults={ "verified":True, "verified_phone":True,})
			CustomerPhone.objects.get(number = o[2], customer=c)
			if created:
				c.set_location_from_address()

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
			cambridge = ZipCode.objects.filter(code="02139")[0]

			m, created = Merchant.objects.get_or_create(phone = m_phone, defaults={'user':u, 'address_1':"15 Pearl St.",'zipcode':cambridge, 'balance':100, 'business_name':"Kwan's Pizza", 'admin':"Kwan"})
			if created:
				print "Cant find Kwan's pizza"
			
			o, created = Offer.objects.get_or_create(merchant=m,title=name,description=description, defaults={'dollar_off':dollar_off, 'time_stamp':time_stamp,'starting_time':time_stamp,'duration':duration,'max_offers':customers})
			o.is_processing=False
			o.save()
			c = Customer.objects.all()[0]
			
			oc, created = OfferCode.objects.get_or_create(code=code,
																										offer=o, 
																										customer=c, 
																										time_stamp=datetime.now(), 
																										expiration_time=datetime.now() + timedelta(minutes=o.duration))

	def create_geo_merchants(self):
		zip_reader = [
                                        ["US", "02135", "Brighton", "Massachusetts", "MA", "kool4@mit.edu", "Kwan's Pizza4", "313 Allston Street", "", "-42.23432", "42.23432", "617-000-0004"],
                                        ["US", "94002", "Belmont", "California", "CA", "kool5@mit.edu", "Kwan's Pizza5", "1000 Continentals Way", "", "-42.23432", "42.23432", "617-000-0005"],
                                        ["US", "10026", "Manhattan", "New York", "NY", "kool6@mit.edu", "Kwan's Pizza6", "", "", "-42.23432", "42.23432", "617-000-0006"],
                                        ["US", "01101", "Springfield", "Massachusetts", "MA", "kool7@mit.edu", "Kwan's Pizza7", "", "", "-42.23432", "42.23432", "617-000-0007"],]



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
		for row in zip_reader:
			u, created = User.objects.get_or_create(username=row[5], email=row[5])
			u.set_password("hello")
			u.is_active=True
			u.save()
			phone = parse_phone_number(row[11])

			zipcode = ZipCode.objects.filter(code="%s" % row[1])[0]
			m, created = Merchant.objects.get_or_create(user=u, address_1="%s" % row[7],zipcode=zipcode, phone=phone,  business_name=row[6], admin="Kwan")
			m.set_location_from_address()
			MerchantPhone.objects.create(number=phone,merchant=m)
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

			cambridge = ZipCode.objects.filter(code="02139")[0]
			m, created = Merchant.objects.get_or_create(user=u, address_1="15 Pearl St.",zipcode=cambridge, phone=phone, business_name=row[6], admin="Kwan")
			m.set_location_from_address()

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

		print settings		
		self.create_merchants()

		self.create_customers()
#		fixture = AutoFixture(Feature)
#		features = fixture.create(10)

#		fixture = AutoFixture(Offer)
#		offers = fixture.create(10)
#		for o in offers:
#			fixture = AutoFixture(OfferCode)
#			codes = fixture.create(10)
		self.create_offers()
		webuy, created = Site.objects.get_or_create(name="Shoppley", domain="shoppley.com")

		webuy, created = Site.objects.get_or_create(name="Shoppley", domain="webuy-dev.mit.edu")
		print "site created",Site.objects.count()

		print Site.objects.all()

	
	def test_redistribute(self):
		#self.create_geo_customers()
		cmd = Command()
		cmd.DEBUG = True
		settings.DEBUG=True
		msg1={"from":"6170000002", "text":"#offer test redistribute"}
		cmd.test_handle(msg1)
		o = Offer.objects.get(description="test redistribute")
		print o
		print o.offercode_set.all().values_list('customer',flat=True)
		for c in o.offercode_set.all().values_list('customer',flat=True):	
			print Customer.objects.get(pk=c).phone, pretty_datetime(OfferCode.objects.filter(customer__pk=c, offer__id = o.id)[0].expiration_time)
		self.create_more_customers()
		print "redistributing..."
		track = o.trackingcode.code
		msg2={"from":"6170000002", "text":"#reoffer  %s" % track}
		cmd.test_handle(msg2)
		print o.offercode_set.all().values_list('customer',flat=True)
		for c in o.offercode_set.all().values_list('customer',flat=True):	
			print Customer.objects.get(pk=c).phone, pretty_datetime(OfferCode.objects.filter(customer__pk=c, offer__id=o.id)[0].expiration_time)

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


	def test_transaction(self):
		user = Customer.objects.all()[0]
		t = Transaction.objects.create(dst  = user , time_stamp=datetime.now(), ttype="MOD", 
						offercode = OfferCode.objects.all()[0],
						offer = Offer.objects.all()[0])
		
		self.assertEqual(t.amount , -20)
		#print oc.offer
		print t
		print user
 		self.assertEqual(Merchant.objects.all()[0].balance,200)
		self.assertEqual(Customer.objects.all()[0].balance, 100)

	def test_offer_cycle(self):
		"""
			submit some offers and check receiving of offers
			then redeem the offers
		"""

		self.assertEqual(Merchant.objects.all().count(), 1)

		uname = "kool@mit.edu"
		password = "hello"

		m = Merchant.objects.get(business_name="Kwan's Pizza")
		self.assertEqual(m.is_customer(), False)

		print "Authenticated:", m.user.is_authenticated()

		cmd = reverse("shoppleyuser.views.login_modal")
		params = {"username": uname, 
					"password": password}
		response = self.post_json(cmd, params)
		self.assertEqual(response["result"], "1")

		self.assertEqual(m.user.is_active, True)
		print m.user.get_all_permissions()
		print "Authenticated:", m.user.is_authenticated()

		success = self.client.login(username=uname, password=password)
		self.assertEqual(success, True)

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
		self.assertEqual(response["result"], "-1")

		params = {'name': '$5 off the bill',
					'description': '',
					'now': True,
					'dollar_off': '5',
					'max_offers': 50,
					'duration': 90,
				}
		# default duration 90 minutes

		response = self.post_json( cmd, params )
		self.assertEqual(response["result"], "1")


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
		self.assertEqual(response["result"], "1")
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
		self.assertEqual(response["result"], "1")
		offer_id2 = response["offer_id"]
		print "Offer 2 sent to:", response["num_sent"]

		params = {'name': '$20 off dress shoes',
			'description': 'You get $20 off pants next 60 minutes',
			'dollar_off': '20',
			'duration': '70',
			'max_offers': 50,
			'now': True}
		response = self.post_json( cmd, params )
		self.assertEqual(response["result"], "1")
		offer_id3 = response["offer_id"]
		print "Offer 3 sent to:", response["num_sent"]


		# failed offer, no money specified
		params = {'name': '5% off pants',
			'description': 'You get 5% off pants next 60 minutes',
			'duration': '60',
			'now': False}
		response = self.post_json( cmd, params )
		self.assertEqual(response["result"], "-1")

		# check if offers generated
		offers1 = OfferCode.objects.filter(offer=offer_id1).count()
		self.failIfEqual(offers1, 0)		

		# check if offers generated
		offers2 = OfferCode.objects.filter(offer=offer_id2).count()
		self.failIfEqual(offers2, 0)		
	
		# check if offers generated
		offers3 = OfferCode.objects.filter(offer=offer_id3).count()
		self.failIfEqual(offers3, 0)		
		
	def test_geo_integration(self):
		cmd = Command()
		cmd.DEBUG = True
                settings.DEBUG=True
		self.create_geo_merchants()
		self.create_geo_customers()

	def test_new_txt(self):
		cmd = Command()
		dcmd = DCommand()
		self.create_geo_merchants()
		self.create_geo_customers()
		cmd.DEBUG=True
		settings.DEBUG=True

		print Customer.objects.values_list("user__username", "customerphone__number")	
		print Merchant.objects.values_list("user__username", "phone")
		print MerchantPhone.objects.all()	
		msg1= {"from": "615-000-0001", "text": "#signup "}
		error = False
		try:
			cmd.test_handle(msg1)
		except CommandError:
			error =True
		self.assertEqual(error, True)
		msg1= {"from": "615-000-0001", "text": "#signup smengl@mit.edu"}
		error = False
		try:
			cmd.test_handle(msg1)
		except CommandError:
			error =True
		self.assertEqual(error, True)

		msg1= {"from": "615-000-0001", "text": "#signup smengl@mit.edu 02139"}
		cmd.test_handle(msg1)


		print Customer.objects.values_list("user__username", "customerphone__number")
		msg2= {"from": "615-000-0010", "text": "#m seakmeng_l@yahoo.com 02139"}
		error = False
		try:
			cmd.test_handle(msg2)
		except CommandError:
			error = True
		self.assertEqual(error , True)
		msg2= {"from": "615-000-0010", "text": "#m seakmeng_l@yahoo.com	02139 meng's biz"}
		cmd.test_handle(msg2)
		print MerchantPhone.objects.all()

		MerchantPhone.objects.create(number="615-000-0011", merchant=Merchant.objects.get(phone="6150000010"))

		msg3={"from": "615-000-0010", "text": "#offer "}
		error= False
		try:
			cmd.test_handle(msg3)
		except CommandError:
			error = True
                self.assertEqual(error , True)
		msg3= {"from": "615-000-0010", "text": "#offer meng's pizza1"}
		cmd.test_handle(msg3)
		dcmd.handle_noargs()

		print MerchantPhone.objects.all()
		msg3= {"from": "615-000-0011", "text": "#offer meng's pizza2"}
		cmd.test_handle(msg3)
		dcmd.handle_noargs()


		msg4= { "from": "615-000-0011", "text": "#balance"}
		cmd.test_handle(msg4)
		msg4= {"from": "615-000-0010", "text": "#balance"}
		cmd.test_handle(msg4)


		o = Offer.objects.get(description="meng's pizza1")
		o2 = Offer.objects.get(description="meng's pizza2")

		msg5= {"from": "615-000-0010", "text": "#status"}
		cmd.test_handle(msg5)
		msg5= {"from": "615-000-0011", "text": "#status"}
		cmd.test_handle(msg5)
		msg5= {"from": "615-000-0011", "text": "#status %s %s" % (o.trackingcode.code, o.trackingcode.code)}
		cmd.test_handle(msg5)
		msg5 = {"from": "615-000-0011", "text": "#status xxxxx"}
		error = False
		try:
			cmd.test_handle(msg5)
		except CommandError:
			error = True
		self.assertEqual(error, True)
		msg6= {"from": "615-000-0001", "text": "#info"}
		cmd.test_handle(msg6)

		c = Customer.objects.get(customerphone__number="6150000001")
		msg6= {"from": "615-000-0001", "text": "#info %s" % c.offercode_set.filter(offer=o)[0].code}
		cmd.test_handle(msg6)
		msg6= {"from": "615-000-0001", "text": "#info %s %s" % (c.offercode_set.filter(offer=o)[0].code, c.offercode_set.filter(offer=o2)[0].code)}
		cmd.test_handle(msg6)

		msg1= {"from": "615-000-0002", "text": "#signup seakmeng90@gmail.com 02139"}
		cmd.test_handle(msg1)

		msg7= {"from": "615-000-0001", "text": "#forward %s %s" % (c.offercode_set.filter(offer=o)[0].code, "615-000-0002 615-00-0003")}
		error= False
		try:
			cmd.test_handle(msg7)
		except CommandError:
			error=True
		self.assertEqual(error,True)
		self.assertEqual(c.customer_friends.count(),0)

		msg7= {"from": "615-000-0001", "text": "#forward %s %s" % (c.offercode_set.filter(offer=o)[0].code, "615-000-0002 6150000003")}
		cmd.test_handle(msg7)
		self.assertEqual(c.customer_friends.count(),2)

		msg7= {"from": "615-000-0001", "text": "#forward %s %s" % (c.offercode_set.filter(offer=o)[0].code, "615-000-0002 6150000003")}
		cmd.test_handle(msg7)
		self.assertEqual(c.customer_friends.count(),2)

		msg7= {"from": "615-000-0002", "text": "#forward %s %s" % (c.offercode_set.filter(offer=o)[0].code, "615-000-0002 6150000003")}
		#cmd.test_handle(msg7)
		error = False
		try:
			cmd.test_handle(msg7)

		except CommandError:
			error = True
		self.assertEqual(error, True)
		self.assertEqual(c.customer_friends.count(),2)

		print Customer.objects.values_list("customerphone__number", "offer_count")

		msg8= {"from": "615-000-0010", "text": "#offer meng's pizza3"}
		cmd.test_handle(msg8)
		dcmd.handle_noargs()
		print Customer.objects.values_list("customerphone__number", "offer_count")

		msg8= {"from": "615-000-0002", "text": "#stop"}
		cmd.test_handle(msg8)
		msg9= {"from": "615-000-0010", "text": "#offer meng's pizza4"}
		cmd.test_handle(msg9)
		dcmd.handle_noargs()
		print Customer.objects.values_list("customerphone__number", "offer_count")
		msg8= {"from": "615-000-0002", "text": "#start"}
		cmd.test_handle(msg8)
		msg9= {"from": "615-000-0010", "text": "#offer meng's pizza5"}
		cmd.test_handle(msg9)
		dcmd.handle_noargs()
		print Customer.objects.values_list("customerphone__number", "offer_count")

		msg9= {"from": "615-000-0010", "text":"#balance"}
		cmd.test_handle(msg9)

		msg10={"from": "615-000-0010", "text":"#redeem xxxx 615-000-0001"  }
		error = False
		try:
			cmd.test_handle(msg10)
		except CommandError:
			error = True	
		self.assertEqual(error, True)
		msg10={"from": "615-000-0010", "text":"#redeem %s 615-000-0002" %  c.offercode_set.filter(offer=o)[0].code }
		error = False
		try:

			cmd.test_handle(msg10)
		except CommandError:
			error = True
		self.assertEqual(error, True)

		msg10={"from": "615-000-0010", "text":"#redeem %s 615-000-0001" %  c.offercode_set.filter(offer=o)[0].code }
		cmd.test_handle(msg10)
		msg10={"from": "615-000-0010", "text":"#redeem %s 615-000-0001" %  c.offercode_set.filter(offer=o)[0].code }
		error = False
		try:
			cmd.test_handle(msg10)
		except CommandError:
			error = True
		self.assertEqual(error, True)

		msg11={"from": "615-000-0010", "text": "#balance"}
		cmd.test_handle(msg11)
		msg11={"from": "615-000-0001", "text": "#balance"}
		cmd.test_handle(msg11)
		msg11={"from": "615-000-0002", "text": "#balance"}
		cmd.test_handle(msg11)
		c2 = Customer.objects.get(customerphone__number="6150000002")
		
		msg10={"from": "615-000-0010", "text":"#redeem %s 615-000-0002" %  c2.offercode_set.filter(offer=o)[0].code }
		cmd.test_handle(msg10)
		msg11={"from": "615-000-0010", "text": "#balance"}
		cmd.test_handle(msg11)
		msg11={"from": "615-000-0001", "text": "#balance"}
		cmd.test_handle(msg11)
		msg11={"from": "615-000-0002", "text": "#balance"}
		cmd.test_handle(msg11)

		cmd.update_expired()
		print "---------------done----------"
		o.expired_time = datetime.now()
		o.save()
		o2.expired_time = datetime.now()
		o2.save()
		cmd.update_expired()
		print o.offercode_set.values_list("code")


		msg12={"from": "615-000-0001", "text":"#info %s" % c.offercode_set.filter(offer=o)[0].code[0:6]}
		cmd.test_handle(msg12)
		msg12={"from": "615-000-0001", "text":"#forward %s 615-000-0005" % c.offercode_set.filter(offer=o)[0].code[0:6]}
		cmd.test_handle(msg12)
		msg12={"from": "615-000-0010", "text":"#redeem %s 615-000-0001" %  c.offercode_set.filter(offer=o)[0].code[0:6]}
		cmd.test_handle(msg12)

		cmd.update_expired()
		print o.offercode_set.values_list("code")


	def test_txt_messages(self):
		cmd = Command()
		cmd.DEBUG = True
		settings.DEBUG=True
		self.failIfEqual(cmd.DEBUG,False)
		self.create_geo_merchants()
		self.create_geo_customers()
		msg1= {"from":"8043329436", "text":"#signup smengl@mit.edu 02139"}
		pattern = "#"+Word(alphas+"_") + ZeroOrMore(Word(alphanums+"!@#$%^&*()_+=-`~,./<>?:;\'\"{}[]\\|"))
		eles=pattern.parseString(msg1["text"])
		del eles[0]
		self.assertEqual(len(eles),3)
		self.assertEqual(eles[0],"signup")
		self.assertEqual(eles[1],"smengl@mit.edu")
		self.assertEqual(eles[2],"02139")


		msg2={"from":"8043329436", "text":"#merchant m1@mit.edu 02139 m1 gasoline pump"}
		cmd.test_handle(msg2)
		cambridge=ZipCode.objects.filter(code="02139")[0]
		
		m= Merchant.objects.filter(zipcode=cambridge,business_name="m1 gasoline pump")
		
		self.assertEqual(m.count(),1)
		print m[0].user.password, m[0].user.username
		#count=0
		#for i in OfferCode.objects.all():
		#	print str(count), i
		#	count = count+1

		print "************* TEST 0: PATTERN UNMATCHED ***************"
		msg0={"from":"6170000001", "text":"offer Pizza free all day"}
		cmd.test_handle(msg0)
		msg0={"from":"6170000001", "text":"info"}
		cmd.test_handle(msg0)
		msg0={"from":"6170000001", "text":"forward 11223 11223334"}
		cmd.test_handle(msg0)
		msg0={"from":"6170000001", "text":"stop"}
		cmd.test_handle(msg0)
		msg0={"from":"6170000001", "text":"start"}
		cmd.test_handle(msg0)
		msg0={"from":"6170000001", "text":"signup test@a.com 02139"}
		cmd.test_handle(msg0)
		msg0={"from":"6170000001", "text":"merchant test@a.com 02139 test-merc"}
		cmd.test_handle(msg0)
		msg0={"from":"6170000001", "text":"status"}
		cmd.test_handle(msg0)
		msg0={"from":"6170000001", "text":"redeem 11223 11223334"}
		cmd.test_handle(msg0)
		msg0={"from":"6170000001", "text":"help"}
		cmd.test_handle(msg0)
		print "************* TEST 1 ***************"
		
		msg2={"from":"6170000001", "text":"#offer Pizza free all day 5% off at la verdes all night"}
		self.assertEqual(Offer.objects.filter(description__icontains="Pizza free all day 5%").count(),0)
		merchant = Merchant.objects.get(phone="6170000001")
		initial_balance = merchant.balance
		print "Initial balance = ", initial_balance		
		cmd.test_handle(msg2)
		offer =Offer.objects.filter(description__icontains="Pizza free all day 5%")
		self.assertEqual(offer.count(),1)
		offer = offer[0]

		############## TODO: WHY?????????????????????
		print "Current balance = ", merchant.balance
		print "merchant id = ", merchant.id
		print "current balance =", offer.merchant.balance
		print "merchant id = ", offer.merchant.id
		self.assertEqual(offer.merchant.balance, initial_balance - offer.offercode_set.all().count()*20)
		print offer
		print TrackingCode.objects.get(offer=offer)	
		self.assertEqual(offer.merchant, merchant)
		track = TrackingCode.objects.get(offer = offer).code
		print track
		
		msg2a = {"from":"6170000001", "text":"#balance"}
		cmd.test_handle(msg2a)

		print "************* TEST 2: INFO ***************"
		msg3={"from":"0000000001", "text":"#info 00001 00002 00003"}
		cmd.test_handle(msg3)
		msg4={"from":"0000000001", "text":"#info 00004"}
		error = False
		try:
			cmd.test_handle(msg4)
		except CommandError:
			error = True
		#self.assertTrue(error)

		print "************* TEST 3: STOP ***************"
		msg5={"from":"0000000001", "text": "#stop"}
		cmd.test_handle(msg5)
		c=Customer.objects.filter(phone__iexact=msg5["from"])
		self.assertEqual(c.count(), 1)
		self.assertEqual(c[0].active, False)
		print "************* TEST 4: START ***************"
		msg6={"from":"0000000001", "text": "#start"}
		cmd.test_handle(msg6)
		self.assertEqual(c[0].active, True)

		print "************* TEST 5: FORWARD ***************"

		# sign up the originator
		msg_signup={"from":"0000000001", "text": "#signup c1@mit.edu 02139"}
		cmd.test_handle(msg_signup)
		forwarder = Customer.objects.filter(phone__iexact="0000000001")
		self.assertEqual(forwarder.count(),1)

		msg7={"from":"0000000001", "text": "#forward 00002 000-000-0002 000-000-0001 000-000-0003"}
		forwarder = Customer.objects.filter(phone__iexact="0000000001")
		self.assertEqual(forwarder[0].customer_friends.count(),0)

		code = OfferCode.objects.get(code="00002")
		print "offercode", code, code.customer.phone 

		cmd.test_handle(msg7)
		forwarder = Customer.objects.filter(phone__iexact="0000000001")
		self.assertEqual(forwarder.count(),1)
		forwarder = forwarder[0]
		self.assertEqual(forwarder.customer_friends.count(),2)
		receiver = Customer.objects.filter(phone__iexact="0000000002")
		self.assertEqual(receiver.count(),1)
		receiver = receiver[0]
		self.assertEqual(receiver.customer_friends.count(),1)
		self.assertEqual(forwarder in receiver.customer_friends.all(),True)

		receiver = Customer.objects.filter(phone__iexact="0000000003")
		self.assertEqual(receiver.count(),1)
		receiver = receiver[0]
		self.assertEqual(receiver.customer_friends.count(),1)
		self.assertEqual(forwarder in receiver.customer_friends.all(),True)

		oc_ori = OfferCode.objects.filter(code = "00002")
		self.assertEqual(oc_ori.count(),1)
		
		oc = OfferCode.objects.filter(offer__id=oc_ori[0].offer.id,customer__id=receiver.id)
		self.assertEqual(oc.count(),1)
		oc = oc[0]
		self.assertEqual(oc.forwarder.id,forwarder.id)
		print "ori_code: %s" % oc_ori[0].code, "code: %s " % oc.code
		self.assertNotEqual(oc.code,oc_ori[0].code)
		print "************* TEST 5a: FORWARD TO NON-CUSTOMER***************"

		msg7a={"from":"0000000001", "text": "#forward 00002 000-000-0100"}
		cmd.test_handle(msg7a)
		forwarder = Customer.objects.filter(phone__iexact="0000000001")
		self.assertEqual(forwarder.count(),1)
		forwarder = forwarder[0]
		self.assertEqual(forwarder.customer_friends.count(),3)
		rec_user = User.objects.filter(username__iexact="0000000100")
		self.assertEqual(rec_user.count(),1)
		print rec_user[0].email
		self.assertEqual(rec_user[0].email,"")
		receiver = Customer.objects.filter(phone__iexact="0000000100")
		self.assertEqual(receiver.count(),1)
		receiver = receiver[0]
		self.assertEqual(receiver.customer_friends.count(),1)
		self.assertEqual(forwarder in receiver.customer_friends.all(),True)
		oc2 = OfferCode.objects.filter(offer__id=oc_ori[0].offer.id,customer__phone="0000000100")
		self.assertEqual(oc2.count(),1)
		oc2 = oc2[0]
		self.assertEqual(oc2.forwarder.id,forwarder.id)
		self.assertEqual(oc2.customer.id,receiver.id)
		print "ori_code: %s" % oc_ori[0].code, "code: %s " % oc2.code
		self.failIfEqual(oc2.code,oc_ori[0].code)
		self.failIfEqual(oc2.code,oc.code)
		print "************* TEST 5b: FORWARD REACH LIMIT***************"

		msg7b={"from":"0000000001", "text": "#forward 00002 0000000100"}
		cmd.test_handle(msg7b)

		print "************* TEST 5c: FORWARD A CODE THE CUSTOMER DOES NOT OWN***************"
		# forward code not the customer's
		msg7c={"from":"0000000002", "text": "#forward 00002 0000000100"}
		offercode = OfferCode.objects.get(code = "00002")
		customer = Customer.objects.get(phone__iexact="0000000002")
		self.failIfEqual(offercode.customer, customer)

		#f_state = ForwardState.objects.filter(customer=customer,offer=offercode.offer)
		error = False		
		try:
			cmd.test_handle(msg7c)
		except CommandError:
			error = True
		self.assertTrue(error)
		self.assertEqual(customer.customer_friends.count(),1)
		# forward code that does not exist
		print "************* TEST 5d: FORWARD A CODE THAT DOES NOT EXIST***************"
		msg7d={"from":"0000000002", "text": "#forward 0000X 0000000100"}
		error = False
		try:
			cmd.test_handle(msg7d)
		except CommandError:
			error = True
		self.assertTrue(error)
		self.assertEqual(customer.customer_friends.count(),1)
		# forward to someone who already has the offer
		print "************* TEST 5e: FORWARD TO SOMEONE WHO ALREADY HAS THE OFFER***************"
		msg7e={"from":"0000000002", "text": "#forward 00001 0000000100"}
		error = False
		try:
			cmd.test_handle(msg7e)
		except CommandError:
			error= True
		self.assertTrue(error)
		self.assertEqual(customer.customer_friends.count(),1)
		print "************* TEST 6: REDEEM ***************"
		msg8={"from":"6170000001", "text": "#redeem 00001 0000000001"}
		customer = Customer.objects.filter(phone__iexact="0000000001")
		merchant = Merchant.objects.get(phone__iexact="6170000001")
		self.assertEqual(customer.count(),1)
		customer = customer[0]
		c_init = customer.balance
		m_init = merchant.balance
		print "merchant's initial balance=",m_init
		print "customer's initial balance=",c_init
		oc = OfferCode.objects.filter(code__iexact="00001")
		self.assertEqual(oc.count(),1)
		oc = oc[0]

		cmd.test_handle(msg8)		
		customer = Customer.objects.get(phone__iexact="0000000001")
		merchant = Merchant.objects.get(phone__iexact="6170000001")
		self.assertEqual(merchant.balance, m_init+ 10)
		self.assertEqual(customer.balance, c_init+ 10)
		self.failIfEqual(oc.redeem_time,"")

		receiver = Customer.objects.get(phone__iexact="0000000002")
		offercode = OfferCode.objects.get(customer=receiver,offer = OfferCode.objects.get(code="00002").offer)
		msg8a={"from":"6170000002", "text": "#redeem %s 0000000002" % offercode.code}
		f_init = offercode.forwarder.balance
		c_init = receiver.balance
		m_init = offercode.offer.merchant.balance
		print "merchant's initial balance=",m_init
		print "customer's initial balance=",c_init
		print "forwarder's initial balance=",f_init
		cmd.test_handle(msg8a)		

		print "merchant's  balance=",Merchant.objects.get(phone__iexact="6170000002").balance
		print "customer's  balance=",Customer.objects.get(phone__iexact="0000000002").balance
		print "forwarder's  balance=",Customer.objects.get(phone__iexact="0000000001").balance
		
		self.assertEqual(Merchant.objects.get(phone__iexact="6170000002").balance, m_init+ 10)
		self.assertEqual(Customer.objects.get(phone__iexact="0000000002").balance, c_init+ 10)
		self.assertEqual(Customer.objects.get(phone__iexact="0000000001").balance, f_init+ 10)
		print "************* TEST 6a: REDEEM MERCHANT IS NOT THE OWNER OF THE OFFER***************"
		# merchant is not the owner of the offer
		msg8a={"from":"6170000001", "text": "#redeem 00002 0000000001"}
		customer = Customer.objects.filter(phone__iexact="0000000001")
		self.assertEqual(customer.count(),1)
		customer = customer[0]
		oc = OfferCode.objects.filter(code__iexact="00002")
		self.assertEqual(oc.count(),1)
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
		msg6b={"from":"6170000001", "text": "#redeem 0000X 0000000001"}
		error=False
		try:
			cmd.test_handle(msg6b)
		except CommandError:
			error= True
		self.assertTrue(error)


		print "************* TEST 6d: REDEEM CODE REUSE**************"
		msg6d={"from":"6170000001", "text": "#redeem 00001 0000000001"}
		error = False		
		try:
			cmd.test_handle(msg6d)
		except:
			error = True
		self.assertTrue(error)

		print "************* TEST 6e: REDEEM WITH NO PARAMS OR WRONG PARAMS **************"
		msg6e={"from":"6170000001", "text": "#redeem"}
		error = False		
		try:
			cmd.test_handle(msg6e)
		except CommandError, e:
			self.assertEquals(str(e), "Merchant attempted redeem command without offer code or phone number: #redeem")
			
		msg6e2={"from":"6170000001", "text": "#redeem 00001"}
		error = False		
		try:
			cmd.test_handle(msg6e2)
		except CommandError, e:
			self.assertEquals(str(e), "Merchant attempted redeem command without offer code or phone number: #redeem 00001")
	

		print "************* TEST 6c: REDEEMER != CODE'S CUSTOMER***************"
		offer = OfferCode.objects.get(code="00002").offer
		customer2 = Customer.objects.get(phone="0000000002")
		OfferCode(offer=offer,code="000X2",customer=customer2,time_stamp=datetime.now(),expiration_time=datetime.now() + timedelta(minutes=offer.duration)).save()
		# redeemer and code's owner are different
		msg8c={"from":"6170000002", "text": "#redeem 000X2 0000000001"}
		error = False
		try:
			cmd.test_handle(msg8c)
		except CommandError:
			error = True
		self.assertTrue(error)

		print "************* TEST 7: SIGNUP ***************"
		msg9={"from":"0000000010", "text": "#signup s10@mit.edu 02139"}
		self.assertEqual(Customer.objects.filter(phone__iexact=msg9["from"]).count(),0)
		cmd.test_handle(msg9)
		newc=Customer.objects.filter(phone__iexact=msg9["from"])
		self.assertEqual(newc.count(),1)
		self.assertEqual(newc[0].user.email , "s10@mit.edu")
		self.assertEqual(newc[0].phone , "0000000010")

		print "************* TEST 7a: RESIGNUP ***************"
		msg9a={"from":"0000000010", "text": "#signup s10@mit.edu 02139"}
		error = False
		self.assertEqual(Customer.objects.filter(phone__iexact=msg9a["from"]).count(),1)
		cmd.test_handle(msg9a)
		self.assertEqual(Customer.objects.filter(phone__iexact=msg9a["from"]).count(),1)


		print "************* TEST 7b: SIGNUP: reuse EMAIL ***************"
		msg9b={"from":"0000000011", "text": "#signup s10@mit.edu 02139"}
		error = False
		try:
			cmd.test_handle(msg9b)
		except CommandError:
			error = True
		self.assertTrue(error)

		print "************* TEST 7c: SIGNUP: reuse PHONE ***************"
		msg9c={"from":"0000000010", "text": "#signup s11@mit.edu 02139"}
		self.assertEqual(Customer.objects.filter(phone__iexact=msg9c["from"]).count(),1)
		cmd.test_handle(msg9c)
		self.assertEqual(Customer.objects.filter(phone__iexact=msg9c["from"]).count(),1)

		print "************* TEST 8: merchant ***************"
		msg10={"from":"0000000020", "text": "#merchant m20@mit.edu 02139 test Merchant name"} # what if merchant business name contains many words
		cmd.test_handle(msg10)
		tokens = pattern.parseString(msg10["text"])
		newu=User.objects.filter(email=tokens[2], username=tokens[2])
		self.assertEqual(newu.count(),1)
		newm=Merchant.objects.filter(phone__iexact=msg10["from"])
		self.assertEqual(newm.count(),1)
		self.assertEqual(newm[0].business_name,"test Merchant name")

		print "************* TEST 8a: RESIGNUP ***************"
		msg10a={"from":"0000000020", "text": "#merchant m20@mit.edu 02139 test Merchant name"}
		error = False
		self.assertEqual(Merchant.objects.filter(phone__iexact=msg10a["from"]).count(),1)
		cmd.test_handle(msg10a)
		self.assertEqual(Merchant.objects.filter(phone__iexact=msg10a["from"]).count(),1)


		print "************* TEST 8b: SIGNUP: reuse EMAIL ***************"
		msg10b={"from":"0000000021", "text": "#merchant m20@mit.edu 02139 test Merchant name"}
		error = False
		try:
			cmd.test_handle(msg10b)
		except CommandError:
			error = True
		self.assertTrue(error)

		print "************* TEST 8c: SIGNUP: reuse PHONE ***************"
		msg10c={"from":"0000000020", "text": "#merchant m21@mit.edu 02139 test Merchant name"}
		self.assertEqual(Merchant.objects.filter(phone__iexact=msg10c["from"]).count(),1)
		cmd.test_handle(msg10c)
		self.assertEqual(Merchant.objects.filter(phone__iexact=msg10c["from"]).count(),1)

		print "************* TEST 9: STATUS ***************"
		# test phone number isnt in record, and text for info
		msg11={"from":"6170000001", "text":"#status %s" % track}
		cmd.test_handle(msg11)
		offercode= OfferCode.objects.get(customer=Customer.objects.get(phone="0000000001"),offer=TrackingCode.objects.get(code=track).offer)

		msg11a = {"from":"0000000001", "text":"#forward %s 0000000010" % offercode.code}
		cmd.test_handle(msg11a)


		msg11b={"from":"6170000001", "text":"#status %s" % track}
		cmd.test_handle(msg11b)


		print "************* TEST 10: DISTRIBUTE WITH NONACTIVE ***************"
		#cmd.update_expired()
#test expired
# test distribute to nonactive
		customer1= Customer.objects.get(phone="0000000001")
		customer1= Customer.objects.get(phone="0000000002")
		msg12={"from":"0000000001", "text": "#stop"}
		cmd.test_handle(msg12)
		msg13={"from":"0000000002", "text": "#stop"}
		cmd.test_handle(msg13)
		msg14={"from":"6170000002", "text":"#offer All you can eat for $10"}
		cmd.test_handle(msg14)
		
		offer = Offer.objects.get(description="All you can eat for $10")
		self.assertEqual(Customer.objects.filter(verified=True).count()-5, offer.num_init_sentto)
		code = offer.offercode_set.filter(customer = customer1)
		self.assertEqual(code.count(),0)
		code = offer.offercode_set.filter(customer = customer2)
		self.assertEqual(code.count(),0)

		print "**************** TEST 11: Help ************************"
		msg15={"from":"0000000001", "text": "#help"}
		cmd.test_handle(msg15)
		msg16={"from":"6170000002", "text":"#help"}
		cmd.test_handle(msg16)

		print "**************** TEST 12: Update_expired ************************"
		m = Merchant.objects.get(phone="6170000002")
		msg = {"from":"6170000002", "text": "#offer EXpIRED"}
		cmd.test_handle(msg)
		o = Offer.objects.get(merchant = m, description="EXpIRED")
		o.expired_time = datetime.now()
		#o.duration = 0
		o.save()
		print Offer.objects.values_list("expired_time",flat=True)
		self.assertEqual(cmd.update_expired(),1)
		for oc in o.offercode_set.all():
			msg = {"from": "%s" % oc.customer.phone, "text": "#info %s" % oc.code[0:6]}
			cmd.test_handle(msg)
			msg = {"from": "%s" % oc.customer.phone, "text": "#forward %s 1000000000" % oc.code[0:6]}
			cmd.test_handle(msg)
			msg = {"from": "%s" % m.phone, "text": "#redeem %s %s" % (oc.code[0:6], oc.customer.phone)}
			cmd.test_handle(msg)
		
		print "**************** TEST 13: NON_VERIFIED SENT FORWARD ************************"

		c = Customer.objects.filter(verified=False)
		self.assertEqual( c.count(), 1)
		print c
		c = c[0]
		offer = Offer.objects.get(description="All you can eat for $10")
		init_count = offer.offercode_set.count()
		offercode = offer.offercode_set.all()[0]
		msg17 = {"from": "%s" % offercode.customer.phone, "text":"#forward %s %s" % (offercode.code, c.phone)}
		print c.phone, "customer count=", Customer.objects.filter(phone__contains=c.phone).count()
		offer_count = c.offer_count
		cmd.test_handle(msg17)
		
		self.assertEqual(offer.offercode_set.count(), init_count +1)
	
		self.assertEqual(OfferCode.objects.filter(offer=offer,customer=c, forwarder=offercode.customer).count(),1)
		self.assertEqual(offer_count, c.offer_count)

		c.verified=True
		c.save()
		
		count_list = []
		verified=Customer.objects.filter(verified=True).values_list('offer_count', flat=True)
		print Customer.objects.all().values_list('phone',flat=True)
		print "verified=" ,verified
		self.assertEqual(c in Customer.objects.filter(verified=True), True)
		
		msg18={"from":"6170000002", "text":"#offer All you can eat for $20"}
		old_balance = ShoppleyUser.objects.get(phone="6170000002").balance
		cmd.test_handle(msg18)
		i=0
		new_verified=Customer.objects.filter(verified=True).values_list('offer_count', flat=True)
		print "new=" , new_verified
		self.assertEqual(verified.count(),new_verified.count())
		msg19={"from":"6170000002", "text":"#balance"}
		cmd.test_handle(msg19)
		new_balance=  ShoppleyUser.objects.get(phone="6170000002").balance
		offer = Offer.objects.get(description="All you can eat for $20")
		self.assertEqual(old_balance+Transaction.points_table["MOD"]*offer.offercode_set.count(),new_balance)
		print "**************** TEST 14: OFFER SENT TO CUSTOMER REACH LIMIT ************************"
		msg12={"from":"0000000001", "text": "#start"}
		cmd.test_handle(msg12)
		msg13={"from":"0000000002", "text": "#start"}
		cmd.test_handle(msg13)
		for c in Customer.objects.all():
			c.daily_limit=4
			c.save()

		msg18={"from":"6170000001", "text":"#offer All you can eat for $30"}
		old_balance = ShoppleyUser.objects.get(phone=msg18["from"]).balance
		cmd.test_handle(msg18)
		i=0
		new_verified=Customer.objects.filter(verified=True).values_list('offer_count', flat=True)
		print "new=" , new_verified
		self.assertEqual(verified.count(),new_verified.count())
		msg19={"from":"6170000001", "text":"#balance"}
		cmd.test_handle(msg19)
		new_balance=  ShoppleyUser.objects.get(phone="6170000001").balance
		offer = Offer.objects.get(description="All you can eat for $30")
		self.assertEqual(old_balance+Transaction.points_table["MOD"]*offer.offercode_set.count(),new_balance)
		msg19={"from":"6170000001", "text":"#balance"}
		cmd.test_handle(msg19)
		print "**************** TEST 15: MERCHANT NOT ENOUGH POINT ************************"
		msg12={"from":"0000000001", "text": "#start"}
		cmd.test_handle(msg12)
		msg13={"from":"0000000002", "text": "#start"}
		cmd.test_handle(msg13)
		for c in Customer.objects.all():
			c.daily_limit=4
			c.save()

		msg18={"from":"6170000002", "text":"#offer All you can eat for $3"}
		old_balance = ShoppleyUser.objects.get(phone=msg18["from"]).balance
		cmd.test_handle(msg18)
		i=0
		new_verified=Customer.objects.filter(verified=True).values_list('offer_count', flat=True)
		print "new=" , new_verified
		self.assertEqual(verified.count(),new_verified.count())
		msg19={"from":"6170000002", "text":"#balance"}
		cmd.test_handle(msg19)
		new_balance=  ShoppleyUser.objects.get(phone="6170000002").balance
		offer = Offer.objects.get(description="All you can eat for $3")
		self.assertEqual(old_balance+Transaction.points_table["MOD"]*offer.offercode_set.count(),new_balance)
		msg19={"from":"6170000002", "text":"#balance"}
		cmd.test_handle(msg19)
	
		print "**************** TEST 16: CHANGE ZIPCODE ************************"
		print ZipCode.objects.all()
		boston = ZipCode.objects.get(code="02142")
		msg20={"from":"0000000001", "text": "#zipcode 02142"}
		cmd.test_handle(msg20)
		msg20={"from":"6170000001", "text": "#zipcode 02142"}
		cmd.test_handle(msg20)
		msg21={"from":"6170000001", "text":"#offer All you can eat in boston"}
		cmd.test_handle(msg21)

		new_verified=Customer.objects.filter(verified=True).values_list('offer_count', flat=True)
		print "new=" , new_verified
		msg21={"from":"6170000003", "text":"#offer All you can eat in cambridge"}
		cmd.test_handle(msg21)

		new_verified=Customer.objects.filter(verified=True).values_list('offer_count', flat=True)
		print "new=" , new_verified

		print "**************** TEST 17: IWANT  ************************"
		msg22={"from":"0000000001", "text": "#iwant italian food"}

		cmd.test_handle(msg22)
		self.assertEqual(IWantRequest.objects.all().count(),1)
		self.assertEqual(IWantRequest.objects.get(customer=Customer.objects.get(phone="0000000001")).request, "italian food")
		
		print "**************** TEST 18: REDISTRIBUTE  ************************"

		o = Offer.objects.get(description="All you can eat for $3")
		track  = o.trackingcode.code
		offers = Offer.objects.all().count()
		codes = o.offercode_set.all().count()
		print o.offercode_set.all()
		self.create_more_customers()
		msg23={"from":"%s" % o.merchant, "text": "#reoffer %s" % track}
		cmd.test_handle(msg23)
		self.assertEqual(Offer.objects.all().count(),offers)
		print "new", o.offercode_set.all()
		self.assertEqual(codes<o.offercode_set.all().count(),True)

		print "***************TEST 19: VOTE ***************"
		c = Customer.objects.get(phone="0000000001")
		redeemed = c.offercode_set.filter(redeem_time__isnull=False).order_by("-redeem_time")
		print c.offercode_set.order_by("-redeem_time").values_list("offer", "redeem_time")
		msg = {"from": "0000000001", "text": "#yay" }
		cmd.test_handle(msg)
		offer = redeemed[0].offer
		self.assertEqual(offer.vote_set.count(), 1)
		self.assertEqual(offer.vote_set.all()[0].vote, 1)
		msg = {"from": "0000000001", "text": "#nay" }
		cmd.test_handle(msg)
		self.assertEqual(offer.vote_set.count(), 1)
		self.assertEqual(offer.vote_set.all()[0].vote, 1)
	
		offercode = c.offercode_set.filter(redeem_time__isnull=True)[0]
		m = offercode.offer.merchant
		code = offercode.code
		msg = {"from": "0000000001", "text": "#yay %s" % redeemed[0].code }
		cmd.test_handle(msg)
		self.assertEqual(offer.vote_set.count(), 1)
		self.assertEqual(offer.vote_set.all()[0].vote, 1)
        
		msg = {"from": "%s" % m.phone, "text":"#redeem %s %s" % (code, c.phone)}
		cmd.test_handle(msg)
		self.assertEqual(c.offercode_set.filter(redeem_time__isnull=False).count(), 2)
		print c.offercode_set.order_by("-redeem_time").values_list("offer", "redeem_time")

		msg = {"from": "0000000001", "text": "#nay %s" % code }
		cmd.test_handle(msg)
		self.assertEqual(c.vote_set.count(), 2)
		self.assertEqual(c.vote_set.order_by("-time_stamp")[0].vote, -1)
		
		msg = {"from": "0000000001", "text": "#nay 00010" }
		cmd.test_handle(msg)
		self.assertEqual(c.vote_set.count(), 2)

		msg = {"from": "0000000001", "text": "#nay %s xxxxx" % code }
		error = 0
		try:
			cmd.test_handle(msg)
		except CommandError:
			error =1
		self.assertEqual(c.vote_set.count(), 2)
		self.assertEqual(error, 1)



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

