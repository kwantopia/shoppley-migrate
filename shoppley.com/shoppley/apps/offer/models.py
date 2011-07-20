from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext, string_concat

from shoppleyuser.utils import sms_notify, pretty_date, parse_phone_number
from shoppleyuser.models import Customer, Merchant, ShoppleyUser#, Location
from offer.utils import gen_offer_code, gen_random_pw, gen_tracking_code, pretty_datetime, TxtTemplates
from sorl.thumbnail import ImageField

from datetime import datetime, timedelta
import random, string, time

SMS_DEBUG = settings.SMS_DEBUG

# Create your models here.

class Feature(models.Model):
	"""
		Featured location that users can see in their offer
		home page so that they may add to their preferred merchants
	"""
	merchant		= models.ForeignKey(Merchant, related_name="featured")

	time_stamp		= models.DateField()
	description		= models.TextField()

	def __unicode__(self):
		return self.merchant.name
	

class Offer(models.Model):
	merchant		= models.ForeignKey(Merchant, related_name="offers_published")
	title 			= models.CharField(max_length=128, blank=True, help_text="Sexy offer headline. Keep it under 100 characters.")
	description		= models.TextField(blank=True)
	percentage		= models.IntegerField(verbose_name="Percent off (%)", default=0)
	dollar_off		= models.FloatField(verbose_name="Dollar off ($)", default=0)
	
	time_stamp		= models.DateTimeField()
	starting_time	= models.DateTimeField(blank=True, null=True)
	duration		= models.IntegerField(default=90)
	max_offers		= models.IntegerField(verbose_name="Max # of customers", default=50, help_text="Maximum number of customers you want to send to")
	num_init_sentto		= models.IntegerField(default=0) # number of customers the offer was sent to
	num_resent_to		= models.IntegerField(default=0) # number of customers the offer was resent to
	is_merchant_txted	= models.BooleanField(default=False) # True if the merchant was informed the status of the offer after it's expired
	img				= ImageField(upload_to='offers/', blank=True)

	expired = models.BooleanField(default=False)
	expired_time = models.DateTimeField(null=True, blank=True)
	redistributable = models.BooleanField(default=True)
	is_processing = models.BooleanField(default=False)
	redistribute_processing = models.BooleanField(default=False)
	#locations = models.ManyToManyField(Location)
	def __unicode__(self):
		return self.title

	def update_expired_codes(self):
	
		for oc in self.offercode_set.all():
			oc.code = oc.code + self.trackingcode.code
			oc.save()
	
	def expire(self, reset_duration=False):
		"""
			expire the offer
		"""
		#self.expired = True
		if reset_duration:
			# shorten duration manually
			self.duration = 0	
		self.save() 

	def is_active(self):
	#	print "description: ",self.description
		if self.expired_time:
			active = self.expired_time > datetime.now()
		else:
			active = self.starting_time+timedelta(minutes=self.duration) > datetime.now()
		if not active:
			self.expire()
		return active

	def num_forwarded(self):
		return self.offercode_set.count()-self.num_init_sentto-self.num_resent_to

	def num_direct_received(self):
		return self.num_init_sentto+self.num_resent_to

	def num_redeemed(self):
		return self.offercode_set.filter(redeem_time__isnull=False).count()

	def num_received(self):
		return self.offercode_set.count()
	

	def offer_detail(self, past=False):
		"""
			Used to report to merchant mobile phone
		"""
		data = {}

		data["offer_id"] = self.id
		data["title"] = self.title
		data["description"] = self.description
		
		if self.dollar_off != 0:
		    data["amount"] = self.dollar_off
		    data["unit"] = 1
		elif self.percentage != 0:
		    data["amount"] = self.percentage
		    data["unit"] = 2
		
		data["duration"] = self.duration
		
		expire_time = self.starting_time + timedelta(minutes=self.duration)
		data["expires"] = int(time.mktime(expire_time.timetuple())) #pretty_date(expire_time-datetime.now())

		# currently received does not account for forwarded code
		#data["total_received"] = self.num_received()
		recvd = self.num_direct_received()
		data["received"] = recvd 
		redeemed = self.num_redeemed()
		data["redeemed"] = self.num_redeemed() 
		if recvd == 0:
			data["redeem_rate"] = 0
		else:
			data["redeem_rate"] = redeemed/float(recvd)*100

		data["img"] = self.get_image()

		if not past:
			data["redistributable"] = self.redistributable
			data["is_processing"] = self.is_processing
			data["redistribute_processing"] = self.redistribute_processing

		return data
		
	def customer_offer_detail(self, user):
		"""
			Used to report to customer mobile phone
		"""
		location = self.merchant.location.location
		
		offer_detail = {
			"offer_id": self.id,
			"name": self.title,
			"merchant_name": self.merchant.business_name,
			"description": self.description,
			# expires for older version only
			"expires": pretty_date(self.expired_time - datetime.now()),
			"expires_time": int(time.mktime(self.expired_time.timetuple())),
			"phone": self.merchant.phone,
			"address1": self.merchant.address_1,
			"citystatezip": self.merchant.zipcode.citystate(),
			"lat": location.y,
			"lon": location.x,
			"img": self.get_image(),
			"banner": self.merchant.get_banner()
		}
		if self.percentage:
			offer_detail["percentage"] = self.percentage
		elif self.dollar_off:
			offer_detail["dollar_off"] = self.dollar_off
		
		try:
			offercode = OfferCode.objects.get(offer=self, customer=user)
			offer_detail["offer_code_id"] = offercode.id
			offer_detail["code"] = offercode.code
			if offercode.forwarder:
				offer_detail["forwarder"] = str(offercode.forwarder)
		except OfferCode.DoesNotExist:
			pass

		return offer_detail

	def get_image(self):
		if self.img:
			return self.img.url
		else:
			return settings.DEFAULT_OFFER_IMG_URL	

	def gen_tracking_code(self):
		track_code = gen_tracking_code()
		while TrackingCode.objects.filter(code__iexact=track_code):
			track_code = gen_tracking_code()
		TrackingCode.objects.create(
			offer=self,
			code = track_code
		)
		return track_code

	def gen_offer_code(self, customer):
		gen_code = gen_offer_code().lower()
		while self.offercode_set.filter(code__iexact=gen_code):
			gen_code = gen_offer_code()
		self.offercode_set.create (
			customer=customer,
			code=gen_code,
			time_stamp=self.time_stamp,
			expiration_time=self.starting_time+timedelta(minutes=self.duration)
		)
	
	def gen_offer_codes(self, customers):
		"""
			TODO: this part needs to be optimized so that the offer code generation
				does not have a bottle neck
		"""
		count=0
		for customer in customers:
			if customer.is_taking_offers():
				self.gen_offer_code(customer)
				count = count +1
				#print count, customer
				customer.update_offer_count()
		#print "reached " , count
		return count


	def gen_forward_offercode(self,original_code,phone):
	
		#forwarder = OfferCode.objects.filter(code__iexact=original_code)
		
		gen_code = gen_offer_code()
		phone =parse_phone_number(phone)
	
		while (OfferCode.objects.filter(code__iexact=gen_code).count()>0):
			gen_code = gen_offer_code()
		forwarder=original_code.customer
		try: 
			friend = Customer.objects.get(phone=(phone))
			#print phone
			
			o=self.offercode_set.create(
				customer=friend,
				code = gen_code,
				forwarder=forwarder,
				time_stamp=datetime.now(),
				expiration_time=original_code.expiration_time)
			o.save()
			
			forwarder.customer_friends.add(friend)
			return o, None # for existing customer

		except Customer.DoesNotExist:
			# TODO: Need to replace the following with code below
			# create a customer
			# create a username with phone num and create random password

			#print "Creating NEW user with username:", phone
			u, created = User.objects.get_or_create(username=phone)
			u.email=""
			s = string.letters+string.digits
			rand_passwd = ''.join(random.sample(s,6))
			u.set_password(rand_passwd)	
			u.save()
			
			friend, created = Customer.objects.get_or_create(user=u, address_1="", address_2="", zipcode=original_code.customer.zipcode, phone=phone, balance=1000)
			if created:
				friend.set_location_from_address()	
			# send out a new offercode
			o=self.offercode_set.create(
				customer = friend,
				code = gen_code,
				forwarder=forwarder,
				time_stamp=datetime.now(),
				expiration_time=original_code.expiration_time)
			o.save()
			
			forwarder.customer_friends.add(friend)
			return o, rand_passwd  # for new customer

	
	# distribute within x-mile radius from the merchant
	def distribute(self, radius = 5):
		"""
			identify all customers that this offer should go to
			Generate messages, and send messages to them

			Send out offers by generating offer codes

			This should be ideally an asynchronous process
			
			Need to select the users that it will send out to

			- first check for users that are following the merchant
			- then select some extra people that are not following, who
			have not black listed the merchant
			- report back the number of customers being reached
			
		"""
		
		self.is_processing = True
		self.save()
		enough_points = True 
		
		t = TxtTemplates()

		#print "Sending out offers"

		# 70 percent of old customers, 30 percent of new
		max_offers = self.max_offers
		existing_num = int(round(0.7*max_offers))

		merchant = self.merchant
		
		nearby_customers = self.merchant.get_customers_within_miles(radius)
		fans = merchant.fans.filter(pk__in=nearby_customers).exclude(active=False).exclude(verified=False).order_by('?').values_list('pk', flat=True)
		antifans = merchant.antifans.all().values_list('pk', flat=True)
		# TODO: geographically filter
		
		nonfans = Customer.objects.filter(pk__in=nearby_customers).exclude(active=False).exclude(verified=False).exclude(pk__in=fans).exclude(pk__in=antifans).values_list('pk',flat=True)
		#nonfans = Customer.objects.exclude(active=False).exclude(verified=False).exclude(pk__in=fans).exclude(pk__in=antifans).filter(zipcode=merchant.zipcode).values_list('pk', flat=True)

		#print "Num fans:",fans.count()
		#print "Num nonfans:",nonfans.count()
		fan_target = set(list(fans))
		nonfan_target = set(list(nonfans))	
		target = fan_target | nonfan_target
		if len(target) > max_offers:
			target_list = random.sample(target, max_offers)
		else:
			target_list = list(target)

		from worldbank.models import Transaction

		allowed_number =int( self.merchant.balance/abs(Transaction.points_table["MOD"]))
		#print "balance=" ,self.merchant.balance
		#print "allowed_number", allowed_number
		if allowed_number == 0:
			# check if there's enough balance
			enough_points = False

		if len(target_list) > allowed_number:
			target_list = random.sample(target_list, allowed_number)
		sentto = self.gen_offer_codes(Customer.objects.filter(pk__in=target_list))	
		#print "count=" , self.offercode_set.all().count()
		for o in self.offercode_set.all():
			offer_msg = t.render(TxtTemplates.templates["CUSTOMER"]["OFFER_RECEIVED"],{ "merchant":self.merchant.business_name, "title":self.title, "code":o.code })		
			sms_notify(o.customer.phone, offer_msg, SMS_DEBUG)
			transaction = Transaction.objects.create(time_stamp=datetime.now(),
							offer = self,
							offercode = o,
							dst = self.merchant,
							ttype = "MOD")
			transaction.execute()

		self.num_init_sentto =sentto
		self.is_processing = False
		self.expired_time = self.starting_time + timedelta(minutes=self.duration)
		self.save()

	

		
		if enough_points: 
			# number of people sent to, it can be 0 
			return self.num_init_sentto
		else:
			# not enough points to send to
			return -2
			
	def redistribute(self,radius=5):
		self.redistribute_processing=True
		self.save()

		if not self.redistributable:
			# already redistributed, so not allowed any more
			self.redistribute_processing= False
			self.save()
			return -3

		"""
			Offer can be redistributed multiple number of times and all the parameters would be the
			same except extending the duration.

			Need to find targets that have not been reached at all and also have not gone over quota
		"""
		#self.num_resent_to += 5
		#self.save() 
		#print "balance before redist=", self.merchant.balance
		t= TxtTemplates()
		enough_points = True 
		max_resent = 50 - self.num_init_sentto - self.num_resent_to

		# 70 percent of old customers, 30 percent of new

		existing_num = int(round(0.7*max_resent))

		merchant = self.merchant
		
		old_offercodes = self.offercode_set.all()

		# send extension message to old customers
		for oc in old_offercodes:
			#print "before reset" , pretty_datetime(oc.expiration_time), " duration=", self.duration
			oc.expiration_time = datetime.now() + timedelta(minutes=self.duration)
			#print "time added" , datetime.now() + timedelta(minutes=self.duration)
			oc.save()
			
			#print "set expiration to " , pretty_datetime(oc.expiration_time)
			offer_msg = t.render(TxtTemplates.templates["CUSTOMER"]["REOFFER_EXTENSION"],{
						"code": oc.code,
						"title": self.title,
						"merchant": self.merchant.business_name,
						"address": self.merchant.print_address(),
						"expiration": pretty_datetime(oc.expiration_time),})
			sms_notify(oc.customer.phone, offer_msg, SMS_DEBUG)


		# customers who have received the offers
		old_pks = old_offercodes.values_list('customer',flat=True)
		#print "old_pks", old_pks
		nearby_customers = self.merchant.get_customers_within_miles(radius)
		fans = merchant.fans.filter(pk__in=nearby_customers).exclude(active=False).exclude(verified=False).exclude(pk__in=old_pks).order_by('?').values_list('pk', flat=True)
		#fans = merchant.fans.exclude(active=False).exclude(verified=False).exclude(pk__in=old_pks).order_by('?').values_list('pk', flat=True)
		antifans = merchant.antifans.all().values_list('pk', flat=True)

		# TODO: geographically filter
		nonfans = Customer.objects.filter(pk__in=nearby_customers).exclude(active=False).exclude(verified=False).exclude(pk__in=fans).exclude(pk__in=antifans).exclude(pk__in=old_pks).filter(zipcode=merchant.zipcode).values_list('pk', flat=True)

		#print "Num fans:",fans.count()
		#print "Num nonfans:",nonfans.count()
		fan_target = set(list(fans))
		nonfan_target = set(list(nonfans))	
		target = fan_target | nonfan_target
		#print "target: ", target
		if len(target) > max_resent:
			target_list = random.sample(target, max_resent)
		else:
			target_list = list(target)
		#print "target_list: ", target_list
		from worldbank.models import Transaction

		allowed_number =int( self.merchant.balance/abs(Transaction.points_table["MOD"]))
		#print "balance=" ,self.merchant.balance
		#print "allowed_number", allowed_number
		if allowed_number == 0:
			# check if there's enough balance
			enough_points = False

		if len(target_list) > allowed_number:
			target_list = random.sample(target_list, allowed_number)
		resentto = self.gen_offer_codes(Customer.objects.filter(pk__in=target_list))	
		#print "final target_list: ", target_list
		for oc in self.offercode_set.filter(customer__pk__in=target_list):
			oc.expiration_time = datetime.now() + timedelta(minutes=self.duration)
			oc.save()
			offer_msg = t.render(TxtTemplates.templates["CUSTOMER"]["REOFFER_NEWCUSTOMER_RECEIVED"],{ "merchant":self.merchant.business_name, "title":self.title, "code":oc.code })
			
			sms_notify(oc.customer.phone, offer_msg, SMS_DEBUG)
			transaction = Transaction.objects.create(time_stamp=datetime.now(),
							offer = self,
							offercode = oc,
							dst = self.merchant,
							ttype = "MOD")
			transaction.execute()
		
		self.num_resent_to = resentto
		self.redistribute_processing = False
		self.save()
		
		#print "balance after redist=", self.merchant.balance

		# make redistributable false even if the merchant does not have enough
		# points to redistribute.  If the merchant refills more points, they
		# will be able to start new offers instead of being able to redistribute
		# just so they don't keep on trying to redistribute when they don't have
		# enough points and throttle our server.
		self.redistributable = False 
		self.expired_time = datetime.now() + timedelta(minutes=self.duration)
		self.save()

		if enough_points: 
			# number of people sent to, it can be 0 

			self.save()
			return self.num_resent_to

		else:
			# not enough points to send to
			return -2
		return -2

	def redeemers(self):
		"""
			return list of redeemers
		"""
		return self.offercode_set.filter(redeem_time__isnull=False)

## keep track of how many forwardings a customer has initiated on an offer
class ForwardState(models.Model):
	offer 			= models.ForeignKey(Offer)
	customer		= models.ForeignKey(Customer)
	remaining		= models.IntegerField(default=settings.MAX_FORWARDS)
	
	def is_reach_limit(self):
		return self.remaining<=0

	def update(self):
		self.remaining=self.remaining-1
		self.save()

	def allowed_forwards(self,requested_forwards):
		if self.remaining >=requested_forwards:
			return requested_forwards
		else:	
			if self.is_reach_limit():
				return 0
			else:
				return self.remaining

class OfferCode(models.Model):
	offer			= models.ForeignKey(Offer)
	forwarder		= models.ForeignKey(Customer,related_name="forwarder", null=True)
	# TODO: why is customer null=True
	customer		= models.ForeignKey(Customer)
	code			= models.CharField(max_length=32)
	txn_amount = models.FloatField(default=0)
	time_stamp		= models.DateTimeField()
	redeem_time		= models.DateTimeField(null=True, blank=True)
	expiration_time 	= models.DateTimeField()
	feedback		= models.TextField()
	# 1 through 5, 0 is unrated
	rating			= models.IntegerField(default=0)

	def is_valid(self):
		return datetime.now() < time_stamp + timedelta(minutes=self.offer.duration)

	def is_redeemed(self):
		return False if self.redeem_time is None else True

	def redeem(self):
		self.redeem_time = datetime.now()
		self.save()

	def __unicode__(self):
		return self.code + "\n -customer:" + str(self.customer)+"\n -description:"+str(self.offer.description)
	
	def offer_detail(self):
		"""
			Used to report to customer mobile phone
		"""
		offer_detail = {"offer_code_id": self.id,
				"offer_id": self.offer.id,
				"code": self.code,
				"name": self.offer.title,
				"merchant_name": self.offer.merchant.business_name,
				"description": self.offer.description,
				"expires": pretty_date(self.expiration_time-datetime.now()),
				"expires_time": int(time.mktime(self.expiration_time.timetuple())),
				"phone": self.offer.merchant.phone,
				"address1": self.offer.merchant.address_1,
				"citystatezip": self.offer.merchant.zipcode.citystate(),
				"lat": 42.365005, 
				"lon": -71.103329, 
				"img": self.offer.get_image(),
				"banner": self.offer.merchant.get_banner()
				}
		if self.offer.percentage:
			offer_detail["percentage"] = self.offer.percentage
		elif self.offer.dollar_off:
			offer_detail["dollar_off"] = self.offer.dollar_off
		if self.forwarder:
			offer_detail["forwarder"] = str(self.forwarder)

		return offer_detail

	def offer_redeemed(self):
		"""
			Used to report to customer mobile phone
		"""
		offer_detail = {"offer_code_id": self.id,
				"offer_id": self.offer.id,
				"name": self.offer.title,
				"merchant_name": self.offer.merchant.business_name,
				"description": self.offer.description,
				"redeemed": self.redeem_time.strftime("%m-%d-%y %H:%M"),
				"redeemed_time": int(time.mktime(self.redeem_time.timetuple())),
				"txn_amount": "%.2f"%self.txn_amount,
				"feedback": self.feedback,
				"rating": self.rating,
				"phone": self.offer.merchant.phone,
				"address1": self.offer.merchant.address_1,
				"citystatezip": self.offer.merchant.zipcode.citystate(),
				"lat": 42.365005, 
				"lon": -71.103329, 
				"img": self.offer.get_image(),
				"banner": self.offer.merchant.get_banner()
				}
		if self.offer.percentage:
			offer_detail["percentage"] = self.offer.percentage
		elif self.offer.dollar_off:
			offer_detail["dollar_off"] = self.offer.dollar_off
		if self.forwarder:
			offer_detail["forwarder"] = str(self.forwarder)

		return offer_detail



class OfferCodeAbnormal(models.Model):
	ABNORMAL_TYPE = (
		("IV", "Invalid Code"),
		("DR", "Double redemption"),
		("IR", "Internal referral"), 
		("ER", "External referral"),
	)
	time_stamp		= models.DateTimeField()
	ab_type			= models.CharField(max_length=2, choices=ABNORMAL_TYPE)
	offercode		= models.ForeignKey(OfferCode, blank=True, null=True)
	invalid_code	= models.CharField(max_length=32, blank=True)
	referred_customer	= models.ForeignKey(Customer, blank=True, null=True)
	referred_phone	= models.CharField(max_length=20, blank=True, null=True)
	
	
	def __unicode__(self):
		if self.ab_type == "IV":
			return "Invalid code: %s" % self.invalid_code
		else:
			return self.ab_type


class Transaction(models.Model):
	TRANS_TYPE = (
		("MB", "Merchant To Bank"),
		("BM", "Bank To Merchant"),
		("CB", "Customer to Bank"), 
		("BC", "Bank to Customer"),
		("MM", "Merchant to Merchant"),
		("MC", "Merchant to Customer"), 
		("CM", "Customer to Merchant"),
		("CC", "Customer to Customer"),
	)
	time_stamp		= models.DateTimeField()
	trans_type		= models.CharField(max_length=2, choices=TRANS_TYPE)
	amount			= models.IntegerField(default=1)
	src				= models.ForeignKey(ShoppleyUser, null=True, blank=True, related_name="transactions_originated")
	dst				= models.ForeignKey(ShoppleyUser, null=True, blank=True, related_name="transctions_received")

	def __unicode__(self):
		return "%d points from %s to %s" % (self.amount, self.src, self.dst)

class TrackingCode(models.Model):
	offer 			= models.OneToOneField(Offer)
	code			= models.CharField(max_length=32)

	def __unicode__(self):
		return "code: %s for offer: %s" % (self.code, self.offer)

