from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from shoppleyuser.models import Customer, Merchant, ShoppleyUser
from offer.utils import gen_offer_code
import random
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext, string_concat
from shoppleyuser.utils import sms_notify
from sorl.thumbnail import ImageField

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
	percentage		= models.IntegerField(verbose_name="Percent off (%)", blank=True, null=True)
	dollar_off		= models.FloatField(verbose_name="Dollar off ($)", blank=True, null=True)
	
	time_stamp		= models.DateTimeField()
	starting_time	= models.DateTimeField(blank=True, null=True)
	duration		= models.IntegerField(default=90)
	max_offers		= models.IntegerField(verbose_name="Max # of customers", default=50, help_text="Maximum number of customers you want to send to")
	num_init_sentto		= models.IntegerField(default=0) # number of customers the offer was sent to

	img				= ImageField(upload_to='offers/')

	def __unicode__(self):
		return self.title
	
	def is_active(self):
		print "description: ",self.description
		return self.starting_time+timedelta(minutes=self.duration) > datetime.now()

	def print_time_stamp(self):
		return self.time_stamp.strftime("%Y-%m-%d,%I:%M%p")

	def num_redeemed(self):
		return self.offercode_set.filter(redeem_time__isnull=False)

	def num_received(self):
		return self.offercode_set.count()

	def get_image(self):
		if self.img:
			return self.img.url
		else:
			return settings.DEFAULT_OFFER_IMG_URL	

	def gen_tracking_code(self):
		track_code = gen_offer_code()
		while TrackingCode.objects.filter(code__iexact=track_code):
			track_code = gen_offer_code()
		TrackingCode.objects.create(
			offer=self,
			code = track_code
		)
		return track_code

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
		"""
			TODO: this part needs to be optimized so that the offer code generation
				does not have a bottle neck
		"""
		for customer in customers:
			self.gen_offer_code(customer)


	def gen_forward_offercode(self,original_code,phone):
	
		gen_code = gen_offer_code()
		users = ShoppleyUser.objects.all()
		offers = Offer.objects.all()
		while (OfferCode.objects.filter(code__iexact=gen_code).count()>0):
			gen_code = gen_offer_code()
		try: 
			friend = Customer.objects.get(phone__contains=phone)
			o=self.offercode_set.create(
				customer=friend,
				phone = friend.phone,
				code = gen_code,
				forwarder=original_code.customer,
				time_stamp=datetime.now(),
				expiration_time=self.starting_time+timedelta(minutes=self.duration))
			o.save()
			return o, "C" # "C" is for customer

		except Customer.DoesNotExist:
			o=self.offercode_set.create(
				phone = phone,
				code = gen_code,
				forwarder=original_code.customer,
				time_stamp=datetime.now(),
				expiration_time=self.starting_time+timedelta(minutes=self.duration))
			o.save()
			return o, "N" # "N" is for non-customer

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
		fans = merchant.fans.exclude(active=False).order_by('?').values_list('pk', flat=True)
		antifans = merchant.antifans.all().values_list('pk', flat=True)
		# TODO: geographically filter
		nonfans = Customer.objects.exclude(active=False).exclude(pk__in=fans).exclude(pk__in=antifans).filter(zipcode=merchant.zipcode).values_list('pk', flat=True)

		print "Num fans:",fans.count()
		print "Num nonfans:",nonfans.count()
		fan_target = set(list(fans))
		nonfan_target = set(list(nonfans))	
		target = fan_target | nonfan_target
		if len(target) > max_offers:
			target_list = random.sample(target, max_offers)
		else:
			target_list = list(target)

		self.gen_offer_codes(Customer.objects.filter(pk__in=target_list))	
		
		for o in self.offercode_set.all():
			offer_msg = _("[%(code)s] %(title)s by %(merchant)s (reply \"info %(code)s\" for address)")%{ "merchant":self.merchant.business_name, "title":self.title, "code":o.code }			
			if not settings.DEBUG:
				sms_notify(o.customer.phone, offer_msg)
			print o.customer.phone

		self.num_init_sentto =len(target_list)
		self.save()
		return len(target_list) 

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
	time_stamp		= models.DateTimeField()
	redeem_time		= models.DateTimeField(null=True, blank=True)
	expiration_time 	= models.DateTimeField()

	def is_valid(self):
		return datetime.now() < time_stamp + timedelta(minutes=self.offer.duration)

	def is_redeemed(self):
		return not self.redeem_time

	def __unicode__(self):
		return self.code + "\n -customer:" + str(self.customer)+"\n -description"+str(self.offer.description)
	

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
		return "code: %s for offer: %s" (self.code, self.offer)

