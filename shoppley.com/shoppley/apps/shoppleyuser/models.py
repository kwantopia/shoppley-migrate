from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta

# Create your models here.

class Country(models.Model):
	name      = models.CharField(max_length=64)
	code      = models.CharField(max_length=10)

class Region(models.Model):
	name			= models.CharField(max_length=32)
	code			= models.CharField(max_length=10)
	country			= models.ForeignKey(Country)
	
	def __unicode__(self):
		return self.name

class City(models.Model):
	name			= models.CharField(max_length=32)
	region			= models.ForeignKey(Region)
	
	def __unicode__(self):
		return self.name

class ZipCode(models.Model):

	code			= models.CharField(max_length=32)
	city			= models.ForeignKey(City)

	latitude		= models.FloatField(blank=True, null=True)
	longitude		= models.FloatField(blank=True, null=True)

	def __unicode(self):
		return "%s in %s"%(self.code, self.city.name)

class Category(models.Model):
	name			= models.CharField(max_length=32)
	parent			= models.ForeignKey("self")

	def __unicode__(self):
		if self.parent:
			return "%s: %s" % (self.parent.name, self.name)
		else:
			return self.name



class ShoppleyUser(models.Model):
	user			= models.OneToOneField(User)
	address_1		= models.CharField(max_length=64, blank=True)
	address_2		= models.CharField(max_length=64, blank=True)
	zipcode			= models.ForeignKey(ZipCode)
	phone			= models.CharField(max_length=20, blank=True, unique=True)
	categories		= models.ManyToManyField(Category, null=True, blank=True)
	balance			= models.IntegerField(default=0)

	def is_customer(self):
		return hasattr(self, "customer")

	def is_merchant(self):
		return hasattr(self, "merchant")

	def __unicode__(self):
		if self.is_customer():
			if self.user.get_full_name():
				return self.user.get_full_name()
			else:
				return self.user.username
		else:
			return "%s (%s)" % (self.merchant.business_name, self.user.username)
	



class Merchant(ShoppleyUser):
	business_name	= models.CharField(max_length=64, blank=True)
	admin			= models.CharField(max_length=64, blank=True)

	def __unicode__(self):
		return "%s (%s)" % (self.business_name, self.user.username)



class Customer(ShoppleyUser):
	merchant_likes = models.ManyToManyField(Merchant, related_name="fans")
	merchant_dislikes = models.ManyToManyField(Merchant, related_name="antifans")

	def __unicode__(self):
		if self.user.get_full_name():
			return self.user.get_full_name()
		else:
			return self.user.username


class MerchantOfTheDay(models.Model):
	merchant		= models.ForeignKey(Merchant)
	date			= models.DateField()

	def __unicode__(self):
		return "%s - %s" % (self.date, self.merchant.business_name)



