from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from datetime import datetime, timedelta
from sorl.thumbnail import ImageField


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

	def __unicode__(self):
		return "%s in %s"%(self.code, self.city.name)

	def citystate(self):
		return "%s, %s %s"%(self.city, self.city.region.code.upper(), self.code)


class Category(models.Model):
	name			= models.CharField(max_length=32)
	parent			= models.ForeignKey("self",null=True)
	tag			= models.CharField(max_length=32)
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
	phone			= models.CharField(max_length=20, blank=True)
	categories		= models.ManyToManyField(Category, null=True, blank=True)
	balance			= models.IntegerField(default=0)
	active 			= models.BooleanField(default=True)

	def is_customer(self):
		return hasattr(self, "customer")

	def is_merchant(self):
		return hasattr(self, "merchant")

	def print_address(self):
		if self.address_1=="":
			return "No address given"
		else:
			return self.address_1 + "\n" + self.address_2
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
	banner			= ImageField(upload_to="banners/")
	url				= models.URLField(null=True, blank=True)

	
	def save(self, *args, **kwargs):
		if not self.pk:
			
			self.balance = settings.INIT_MERCHANT_BALANCE
			
        	super(Merchant, self).save(*args, **kwargs)

	def __unicode__(self):
#		return "%s (%s %s)" % (self.business_name, self.user.username,self.phone)
		return "%s, %s [%s]" % (self.business_name, self.print_address(), self.phone)
	def get_banner(self):
		if self.banner:
			return self.banner.url
		else:
			return settings.DEFAULT_MERCHANT_BANNER_URL

class Customer(ShoppleyUser):
	FREQUENCY_CHOICES = (
			( 0, 'Every Hour'),
			( 1, 'Every 2 hrs'),
			( 2, '3 times a day'),
			( 3, 'Twice a day'),
			( 4, 'Once a day'),
			( 5, 'Once a week'),
			)

	frequency = models.IntegerField(choices=FREQUENCY_CHOICES, default=4)
	weekdays_only = models.BooleanField(default=False)
	weekends_only = models.BooleanField(default=False)
	merchant_likes = models.ManyToManyField(Merchant, related_name="fans")
	merchant_dislikes = models.ManyToManyField(Merchant, related_name="antifans")


	def save(self, *args, **kwargs):
		if not self.pk:
			
			self.balance = settings.INIT_CUSTOMER_BALANCE
			
        	super(Customer, self).save(*args, **kwargs)

class MerchantOfTheDay(models.Model):
	merchant		= models.ForeignKey(Merchant)
	date			= models.DateField()

	def __unicode__(self):
		return "%s - %s" % (self.date, self.merchant.business_name)


###############
# FOR BETA
##############
class BetaUser(models.Model):
	email			= models.CharField(max_length=64) # must have
	address_1		= models.CharField(max_length=64, blank=True)
	address_2		= models.CharField(max_length=64, blank=True)
	zipcode			= models.ForeignKey(ZipCode)
	phone			= models.CharField(max_length=20, blank=True)
	categories		= models.ManyToManyField(Category, null=True, blank=True)

	def is_betacustomer(self):
		return hasattr(self, "betacustomer")

	def is_betamerchant(self):
		return hasattr(self, "betamerchant")

	def print_address(self):
		if self.address_1=="":
			return "No address given"
		else:
			return self.address_1 + "\n" + self.address_2
	def __unicode__(self):
		if self.is_customer():
			return self.email
		else:
			return "%s (%s)" % (self.merchant.business_name, self.email)

class BetaCustomer(BetaUser):
	pass


class BetaMerchant(BetaUser):
	business_name	= models.CharField(max_length=64, blank=True)
	url				= models.URLField(null=True, blank=True)
	def __unicode__(self):
		return "%s (%s %s)" % (self.business_name,self.email)

