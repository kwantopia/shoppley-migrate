from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from shoppleyuser.models import Customer, Merchant, ShoppleyUser
from offer.utils import gen_offer_code

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
	name			= models.CharField(max_length=128, blank=True)
	description		= models.TextField(blank=True)
	percentage		= models.IntegerField(verbose_name="Percent off (%)", blank=True, null=True)
	dollar_off		= models.FloatField(verbose_name="Dollar off ($)", blank=True, null=True)
	
	time_stamp		= models.DateTimeField()
	starting_time	= models.DateTimeField()
	duration		= models.IntegerField(default=90)
	max_offers		= models.IntegerField(default=50)

	def __unicode__(self):
		return self.name
	
	def is_active(self):
		return self.starting_time+timedelta(minutes=duration) < datetime.now()

	def num_redeemed(self):
		return self.offercode_set.filter(redeem_time__isnull=False)

	def num_received(self):
		return self.offercode_set.count()

	def gen_offer_code(self, customer):
		gen_code = gen_offer_code()
		while self.offercode_set.filter(code__iexact=gen_code):
			gen_code = gen_offer_code()
		self.offercode_set.create (
			customer=customer,
			code=gen_code,
			time_stamp=self.time_stamp,
			expiration_time=self.starting_time+timedelta(minutes=self.duration)
		)
	
	def gen_offer_codes(self, customers):
		for customer in customers:
			self.gen_offer_code(customer)

	def distribute(self):
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
		num_reached = 0
		print "Sending out offers"

		# 70 percent of old customers, 30 percent of new
		max_offers = self.max_offers
		existing_num = int(round(0.7*max_offers))

		merchant = self.merchant
		fans = merchant.fans.order_by('?').values('pk')
		antifans = merchant.antifans.all().values('pk')
		# TODO: geographically filter
		nonfans = Customer.objects.exclude(pk__in=fans).exclude(pk__in=antifans).filter(zipcode=merchant.zipcode).values('pk')

		target = set(list(fans)+list(nonfans))
		if len(target) > max_offers:
			target_list = random.sample(target, max_offers)
		else:
			target_list = list(target)

		self.gen_offer_codes(Customer.objects.filter(pk__in=target_list))	
		
		return len(target_list) 

	def redeemers(self):
		"""
			return list of redeemers
		"""
		return self.offercode_set.filter(redeem_time__isnull=False)


class OfferCode(models.Model):
	offer			= models.ForeignKey(Offer)
	customer		= models.ForeignKey(Customer)
	code			= models.CharField(max_length=32)
	time_stamp		= models.DateTimeField()
	redeem_time		= models.DateTimeField(null=True, blank=True)
	expiration_time = models.DateTimeField()

	def is_valid(self):
		return datetime.now() < time_stamp + timedelta(minutes=self.offer.duration)

	def is_redeemed(self):
		return not self.redeem_time

	def __unicode__(self):
		return self.code
	

class OfferCodeAbnormal(models.Model):
	ABNORMAL_TYPE = (
		("IV", "Invalid Code"),
		("DR", "Double redemption"),
		("IR", "Internal referral"), 
		("ER", "External referral"),
	)
	time_stamp		= models.DateTimeField()
	ab_type			= models.CharField(max_length=2, choices="ABNORMAL_TYPE")
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


