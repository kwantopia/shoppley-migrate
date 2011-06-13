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
	points_table = {"COR":10, "CFR":10,
		"MOR":10, "MOD":-20}

	time_stamp	=models.DateTimeField()
	dst		=models.ForeignKey(ShoppleyUser,related_name="dst_transaction")
	offer		=models.ForeignKey(Offer, blank = True, null = True)
	offercode	=models.ForeignKey(OfferCode, blank=True,null= True)
	ttype		=models.CharField(max_length=3,choices=transaction_TYPES)
	amount		=models.IntegerField(default=0)

	def save(self, *args, **kwargs):
		if not self.pk:
			self.amount = self.points_table[self.ttype]
        	super(Transaction, self).save(*args, **kwargs)


	def __unicode__(self):
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
					"friend": self.offercode.customer,
					"offer":self.offer,
					}
			elif self.ttype=="MOR":
				return _("%(time)s: Merchant %(dst)s earns %(amount)d points after %(customer) redeems offer %(offer)s at his business.") %{
					"time" : self.time_string_l(),
					"dst" : self.dst,
					"amount": self.amount,
					"customer": self.offercode.customer,
					"offer":self.offer,
					}
			elif self.ttype=="MOD":
				return _("%(time)s: Merchant %(dst)s pays %(amount)d points to send  %(offer)s to customer %(customer)s.") % {
					"time" : self.time_string_l(),
					"dst" : self.dst,
					"amount": -1*self.amount,
					"offer":self.offer,
					"customer":self.offercode.customer,
					}
		
	def time_string_l(self):
		return self.time_stamp.strftime("%m-%d %I:%M%p")
	def execute(self):
		#print "In worldbank, init=", self.dst.balance, " amount to be dedcuted=", self.amount
		self.dst.balance= self.dst.balance +self.amount
		#print "In worldbank, afterwards=", self.dst.balance
		self.dst.save()
	
			
