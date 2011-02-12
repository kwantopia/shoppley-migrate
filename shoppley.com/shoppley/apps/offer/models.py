from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta

# Create your models here.

class State(models.Model):
	name			= models.CharField(max_length=32)
	
	def __unicode__(self):
		return self.name


class City(models.Model):
	name			= models.CharField(max_length=32)
	state			= models.ForeignKey(State)
	
	def __unicode__(self):
		return self.name


class Category(models.Model):
	name			= models.CharField(max_length=32)
	parent			= models.ForeignKey("self")

	def __unicode__(self):
		if self.parent:
			return "%s: %s" % (self.parent.name, self.name)
		else:
			return self.name



class ShoppleyUser(User):
	address_1		= models.CharField(max_length=64, blank=True)
	address_2		= models.CharField(max_length=64, blank=True)
	city			= models.ForeignKey(City)
	phone			= models.CharField(max_length=20, blank=True)
	categories		= models.ManyToManyField(Category, null=True, blank=True)
	balance			= models.IntegerField(default=0)

	def is_customer(self):
		return self.hasattr(self, "customer")

	def is_merchant(self):
		return self.hasattr(self, "merchant")

	def __unicode__(self):
		if self.is_customer():
			if self.get_full_name():
				return self.get_full_name()
			else:
				return self.username
		else:
			return self.merchant.business_name
	



class Merchant(ShoppleyUser):
	business_name	= models.CharField(max_length=64, blank=True)
	admin			= models.CharField(max_length=64, blank=True)

	def __unicode__(self):
		return self.username



class Customer(ShoppleyUser):
	merchants_followed	= models.ManyToManyField(Merchant)

	def __unicode__(self):
		return self.username

class Offer(models.Model):
	merchant		= models.ForeignKey(Merchant, related_name="offers_published")
	name			= models.CharField(max_length=128, blank=True)
	description		= models.TextField(blank=True)
	percentage		= models.IntegerField(blank=True, null=True)
	dollar_off		= models.FloatField(blank=True, null=True)
	
	time_stamp		= models.DateTimeField()
	starting_time	= models.DateTimeField()
	duration		= models.IntegerField(default=90)

	def __unicode__(self):
		return self.name
	
	def num_redeemed(self):
		return self.offercode_set.filter(redeem_time__isnull=False)

	def num_received(self):
		return self.offercode_set.count()


class OfferCode(models.Model):
	offer			= models.ForeignKey(Offer)
	user			= models.ForeignKey(Customer)
	code			= models.CharField(max_length=32)
	time_stamp		= models.DateTimeField()
	redeem_time		= models.DateTimeField(null=True, blank=True)

	def is_valid(self):
		return datetime.now() < time_stamp + timedelta(minutes=self.offer.duration)

	def is_redeemed(self):
		return not self.redeem_time

	def __unicode__(self):
		return self.code
	

class MerchantOfTheDay(models.Model):
	merchant		= models.ForeignKey(Merchant)
	date			= models.DateField()

	def __unicode__(self):
		return "%s - %s" % (self.date, self.merchant.business_name)


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




