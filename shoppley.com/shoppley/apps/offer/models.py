from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from shoppleyuser.models import Customer, Merchant, ShoppleyUser

# Create your models here.

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
	expiration_time = models.DateTimeField()

	def is_valid(self):
		return datetime.now() < time_stamp + timedelta(minutes=self.offer.duration)

	def is_redeemed(self):
		return not self.redeem_time

	def __unicode__(self):
		return self.code
	

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


