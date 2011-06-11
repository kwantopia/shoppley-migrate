from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy, string_concat

from shoppleyuser.models import ShoppleyUser
from offer.models import Offer, OfferCode

from datetime import datetime
# Create your models here.

# Default points
# Customers
REDEEM_POINTS = 10  # Points customer earns after redeem
FORWARD_POINTS = 10 # Points a forwarder earns after he forwards an offer and it was redeemed

# Merchants
OFFER_POINTS = -20 # Points a merchant pays to get his offer distributed to a customer
MERCHANT_REDEEM = 10 # Points a merchant earns back after an offercode was redeemed

class Transaction(models.Model):
	transaction_TYPES=(
		# Customers
		("COR", _("Customer Offer Redeem")),
		("CFR", _("Customer Forward Redeemed")),
		# Merchants
		("MOR", _("Merchant Offer Redeemed")),
		("MOD", _("Merchant Offer Distribute")),
	)
	time_stamp	=models.DateTimeField()
	dst		=models.ForeignKey(ShoppleyUser,related_name="dst_transaction")
	amount		=models.IntegerField(default=0)
	offer		=models.ForeignKey(Offer, blank = True, null = True)
	offercodes	=models.ManyToManyField(OfferCode, blank=True,null= True)
	ttype		=models.CharField(max_length=3,choices=transaction_TYPES)
	


	def get_amount(self):
		#self.time_stamp = datetime.now()
		if self.ttype=="COR":
			self.amount = REDEEM_POINTS
		elif self.ttype=="CFR":
			self.amount = FORWARD_POINTS
		elif self.ttype=="MOR":
			self.amount =  MERCHANT_REDEEM
		elif self.ttype=="MOD":
			self.amount =  self.offercodes.all().count()*OFFER_POINTS
		self.save()

	

	def __unicode__(self):
		self.get_amount()
		if self.dst:
			if self.ttype=="COR":
				return _("%(time)s: %(dst)s earns %(amount)d points for redeeming an offer: %(offer)s") % {
					"time": self.time_string_l(),
					"dst": self.dst,
					"amount": self.amount,
					"offer":self.offer,
					}
				
			elif self.ttype=="CFR":
				return _("%(time)s: %(dst)s earns %(amount)d points after %(friend)s redeemed his forwarded offer %(offer)s)") %{
					"time": self.time_string_l(),
					"dst": self.dst,
					"amount": self.amount,
					"friend": self.offercodes.all()[0].customer,
					"offer":self.offer,
					}
			elif self.ttype=="MOR":
				return _("%(time)s: Merchant %(dst)s earns %(amount)d points after %(customer) redeems offer %(offer)s at his business.") %{
					"time" : self.time_string_l(),
					"dst" : self.dst,
					"amount": self.amount,
					"customer": self.offercodes.all()[0].customer,
					"offer":self.offer,
					}
			elif self.ttype=="MOD":
				return _("%(time)s: Merchant %(dst)s pays %(amount) points to send  %(offer)s to %(count)d customers.") % {
					"time" : self.time_string_l(),
					"dst" : self.dst,
					"amount": self.amount,
					"offer":self.offer,
					"count":self.offercodes.all().count(),
					}
		
	def time_string_l(self):
		return self.time_stamp.strftime("%m-%d %I:%M%p")
	def execute(self):
		self.get_amount()
		self.dst.balance= self.dst.balance +self.amount
		self.dst.save()
	
			
