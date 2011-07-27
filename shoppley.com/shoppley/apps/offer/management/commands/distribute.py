from django.core.management.base import NoArgsCommand
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext, string_concat
from django.conf import settings

from shoppleyuser.models import *
from offer.models import *
from shoppleyuser.utils import sms_notify
from offer.utils import TxtTemplates

SMS_DEBUG = settings.SMS_DEBUG
RADIUS = settings.DEFAULT_RADIUS

class Command(NoArgsCommand):

	help = 'Distributes the offers strategically.'

	DEBUG = False
	def notify(self, phone, msg):
		if SMS_DEBUG:
			print _("\"%(msg)s\" sent to %(phone)s") % {"msg":msg, "phone":phone,}
		else:
			sms_notify(phone,msg)

	def handle_noargs(self, **options):
		"""
			read all the offers that have not been distributed, find target users for
			each offer and control how many offers individual gets
		"""

		t = TxtTemplates()

		# get offers that needs processing
		process_areas = Offer.objects.filter(is_processing=True).values('merchant__zipcode').distinct()

		black_words = BlackListWord.objects.all().values_list('word', flat=True)
		# for each area
		for z in process_areas: 
			# for each offer in current area
			for o in Offer.objects.filter(merchant__zipcode=z['merchant__zipcode'], is_processing=True):
				"""
				# check if merchant has enough credits
				"""
				from worldbank.models import Transaction
				allowed_number =int( o.merchant.balance/abs(Transaction.points_table["MOD"]))
				#print "balance=" ,self.merchant.balance
				#print "allowed_number", allowed_number
				if allowed_number == 0:
					# if there isn't enough balance 
					receipt_msg = t.render(TxtTemplates.templates["MERCHANT"]["OFFER_NOTENOUGH_BALANCE"], {"points":o.merchant.balance})
					o.delete()
					continue

				"""
				# check if offer has words in the black list
				"""
				blacked = set(o.title.lower().split()).intersection(black_words) 
				if len(blacked) == 0:
					# if valid content

					"""
					# select target size
					"""
					target_size = 20 if allowed_number > 20 else allowed_number 

					# TODO: need to select 80% of followers and 20% of non-followers

					target_list = []

					# divide up user base in this area and distribute
					users=o.merchant.get_active_customers_miles(RADIUS)
					num_users = len(users)
					if num_users > target_size:
						target_list = random.sample(users, target_size)
					elif num_users > 0:
						target_list = list(users)
					else:
						# no target users that have not received offer
						# select users again among those previously received but haven't
						# filled their quota
						users=Customer.objects.filter(verified=True, active=True, zipcode=z['merchant__zipcode']).values_list('pk', flat=True)

						num_users = users.count()
						if num_users > target_size:
							target_list = random.sample(users, target_size)
						elif num_users > 0:
							target_list = list(users)

					# distribute offer
					sentto = o.gen_offer_codes(Customer.objects.filter(pk__in=target_list))	
					#print "count=" , self.offercode_set.all().count()
					for c in o.offercode_set.all():
						offer_msg = t.render(TxtTemplates.templates["CUSTOMER"]["OFFER_RECEIVED"],{ "merchant":o.merchant.business_name, "title":o.title, "code":c.code })		
						self.notify(c.customer.phone, offer_msg)
						transaction = Transaction.objects.create(time_stamp=datetime.now(),
										offer = o,
										offercode = c,
										dst = o.merchant,
										ttype = "MOD")
						transaction.execute()

					"""
					# Update offer parameters
					"""
					o.num_init_sentto = sentto
					o.expired_time = o.starting_time + timedelta(minutes=o.duration)
					o.save()

					if o.num_init_sentto==0 :
						# no customers
						receipt_msg = t.render(TxtTemplates.templates["MERCHANT"]["OFFER_NO_CUSTOMER"], {"code":o.gen_tracking_code()})

					else:
						"""
						# successfully sent offers
						"""
						receipt_msg = t.render(TxtTemplates.templates["MERCHANT"]["OFFER_SUCCESS"], {
							"time": pretty_datetime(o.time_stamp),
							"offer": o,
							"number": o.num_received(),
							"code": o.gen_tracking_code(),
						})

				else:
					"""
					# black list the offer
					"""
					bo = BlackListOffer(offer=o)
					bo.save()
					for b_word in blacked:
						bo.words.add(BlackListWord.objects.get(word=b_word))
					bo.save()
					receipt_msg = t.render(TxtTemplates.templates["MERCHANT"]["OFFER_BLACKLIST"], {						"unacceptable": ','.join(blacked)
					})

				self.notify(o.merchant.phone, receipt_msg)
				o.is_processing = False
				o.save()


		# process offer redistribute
		"""

								if resentto == 0:
									merchant_msg = t.render(TxtTemplates.templates["MERCHANT"]["REOFFER_ZERO_CUSTOMER"], {"code": offer.trackingcode.code})
								elif resentto==-2:
									merchant_msg = t.render(TxtTemplates.templates["MERCHANT"]["REOFFER_NOTENOUGH_BALANCE"], {"points": su.balance})
								elif resentto==-3:
								else:
									merchant_msg = t.render(TxtTemplates.templates["MERCHANT"]["REOFFER_SUCCESS"], {

										"title" : offer.title,
										"resentto": resentto,
										})

		"""

		# process iwant requests by trying to send the request to merchants of
		# category that matches the request
		for w in IWantRequest.objects.filter(processed=False):
			category = w.match_category()
			# send out the request to those stores in the category
			for m in Merchant.objects.filter(zipcode=w.customer.zipcode, categories=category):
				msg = t.render(TxtTemplates.templates["MERCHANT"]["CUSTOMER_WANTS"],
					{
								"request": w.request,
					})
				self.notify(m.phone, msg)
