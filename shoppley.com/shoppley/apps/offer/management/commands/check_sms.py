from django.core.management.base import NoArgsCommand,CommandError
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext, string_concat
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.conf import settings
from django.contrib.auth.models import User

from emailconfirmation.models import EmailAddress

from shoppleyuser.utils import sms_notify, parse_phone_number,map_phone_to_user
from shoppleyuser.models import ZipCode, Customer, Merchant, ShoppleyUser
from offer.models import Offer, ForwardState, OfferCode, OfferCodeAbnormal, TrackingCode
from offer.utils import gen_offer_code, validateEmail, gen_random_pw, pluralize, pretty_datetime
from googlevoice import Voice
from googlevoice.util import input
from googlevoice.extractsms import extractsms
from pyparsing import *
from random import choice
from datetime import datetime
import re
import string

pattern = "([\w]{%d})[ ]+\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})" % (settings.OFFER_CODE_LENGTH)
redemption_code_re = re.compile(pattern)

# Pattern used to parse text 
customer_pattern = Word(alphas+"_") + ZeroOrMore(Word(alphanums+"!@#$%^&*()_+=-`~,./<>?:;\'\"{}[]\\|"))
merchant_pattern = customer_pattern

# Customer commands:
INFO = "info"
STOP = "stop"
START = "start"
FORWARD = "forward"

# Merchant commands:
REDEEM = "redeem"
OFFER = "offer"
STATUS = "status"

# others
SIGNUP = "signup"
MERCHANT_SIGNUP = "merchant_signup"
HELP = "help"

class Command(NoArgsCommand):
	help = "Check Google Voice inbox for posted offers from merchants"
	DEBUG = False
	def notify(self, phone, msg):
#		if self.DEBUG:
#			print _("\"%(msg)s\" sent to %(phone)s") % {"msg":msg, "phone":phone,}
#		else:
		sms_notify(phone,msg)


	def info(self, offercode):
			return _("[%(code)s]\nmerchant: %(merchant)s; \nexpiration: %(expiration)s; \ndescription: %(description)s;\naddress: %(address)s") %{
								"code" : (offercode.code) ,
								"merchant" : offercode.offer.merchant,
								"expiration":pretty_datetime(offercode.expiration_time)	,
								"description":offercode.offer.description ,
								"address":offercode.offer.merchant.print_address(),
							}
	def update_expired(self):
		
		expired_offers = [x for x in Offer.objects.all() if not x.is_active()]
		for offer in expired_offers:
			sentto = offer.num_init_sentto
			forwarded = offer.offercode_set.filter(forwarder__isnull=False).count()
			redeem = offer.offercode_set.filter(redeem_time__isnull=False).count()
			merchant_msg = _("Your offer %(offer)s was expired. It was sent to %(sentto)s and forwarded to %(forwarded)s other, a total of %(total)s reached. It was redeemed %(redeem)s") %{ "offer": offer,"sentto":pluralize(sentto,"customer"),"forwarded":forwarded,"total":pluralize(int(sentto)+int(forwarded),"customer"),"redeem":pluralize(redeem,"time"),}
			self.notify(offer.merchant.phone,merchant_msg)
		return len(expired_offers)

	def customer_help(self):
		avail_commands = "- info<SPACE>offercode(s): list information about an offercode or offercodes (separated by <SPACE>)\n- forward<SPACE>offercode<SPACE>number(s): forward an offer to your friend or friends separated by <SPACE>\n- stop: stop receiving messages from us\n- start: restart receiving message from us\n- help: list available commands"
		return avail_commands

	def merchant_help(self):
		avail_commands = "- redeem<SPACE>offercode<SPACE>number: redeem a customer's offercode\n- offer<SPACE>name<SPACE>description: start an offer with your business name and offer's description.\n- status<SPACE>trackingcode: check the status of an offer you started"
		return avail_commands
		
	def check_email(self,email,phone):
		try:
			if not validateEmail(email):
				receipt_msg= _('"%s" is not a valid email address. Please provide a new and valid email')%email
				raise CommandError("Invalid email address")			
			user = User.objects.get(username__iexact =email)
			receipt_msg = _('"%s" is already registered with us. Please provide another email.') % email
			self.notify(phone,receipt_msg)
			raise CommandError("Email was already used")
		except User.DoesNotExist:
			return email
		
		### raise user already exist error
	def check_zipcode(self,code,phone):
		try:
			zipcode= ZipCode.objects.get(code=code)
			return code
		except ZipCode.DoesNotExist:
			receipt_msg = _('Zipcode "%s" does not exist. Please provide a correct zipcode.') % code
			self.notify(phone,receipt_msg)
			raise CommandError("Zipcode does not exist")

	def check_phone(self,phone):
		try:
			phone = parse_phone_number(phone)
			customer = Customer.objects.get(phone__icontains=phone)
			receipt_msg=_('"%s" is already registered with us. You can now use our services.') % phone
			self.notify(to,receipt_msg)
			raise CommandError("Phone number was already used")
		except Customer.DoesNotExist:
			return phone
	
	def check_offercode(self,code,phone):
		try:
			offercode = OfferCode.objects.get(code__iexact = code)
			return offercode
		except OfferCode.DoesNotExist:
			receipt_msg = _("Offercode %s does not exist.")% code
			self.notify(phone,receipt_msg)
			OfferCodeAbnormal(time_stamp=datetime.now(), ab_type="IV",invalid_code=code).save()
			raise CommandError("Offercode does not exist")

	def test_handle(self,msg): # take msg: dict("from":phonenumber, "text":text)
		print "new message %s" % msg
		if msg["from"] != "Me":
			su = map_phone_to_user(msg["from"])

			# ****************************** MERCHANT COMMANDS ***********************
			if su and su.is_merchant():
				text = msg["text"].strip()
				
				parsed = merchant_pattern.parseString(text)
				# offer code being redeemed by the customer
				# merchant sends offer code and the customer's phone number

				# --------------------------- REDEEM: "redeem<SPACE>offercode<SPACE>phone number here"---------------
				if parsed[0].lower()==REDEEM:
					offer_code = self.check_offercode(parsed[1],su.phone)
					phone = parse_phone_number(parsed[2])
					if offer_code.offer.merchant != su.merchant:
						receipt_msg = _("Redeem Fail! %s was initiated by a different business, and not by you.") % offer_code.code
						self.notify(su.phone,receipt_msg)
						raise CommandError ("Merchant attempts to redeem an offer he does not own")
					phone = parse_phone_number(parsed[2])
					try:
						current_time = datetime.now()
						print "total =" , OfferCode.objects.filter(code__iexact=offer_code.code)
						offercode_obj = OfferCode.objects.filter(expiration_time__gt=current_time, 
							time_stamp__lt=current_time).get(code__iexact=offer_code.code)
						# The offer code is a valid code, but it might come from referrals
						try:
							# Does the phone belong to a registered customer?
							customer = Customer.objects.get(phone__contains=phone)
							if offercode_obj.customer == customer:
								if not offercode_obj.redeem_time:
									offercode_obj.redeem_time = current_time
									offercode_obj.save()
									receipt_msg = _("%(offer_code)s is a valid offer code! Redeemed by %(customer)s.") % {
										"offer_code": offer_code.code,
										"customer": offercode_obj.customer
									}
									self.notify(su.phone, receipt_msg)
									customer_msg = _("You have successfully redeemed your code at %(merchant)s.") %{
										"merchant": su.merchant.business_name
									}
									self.notify(phone, customer_msg)
								else:
									receipt_msg = _("Code reuse! %(offer_code)s was redeemed by %(customer)s at %(time)s.") % {
										"offer_code": offer_code.code,
										"customer": offercode_obj.customer,
										"time": offercode_obj.redeem_time,
									}
									self.notify(su.phone, receipt_msg)
									OfferCodeAbnormal(time_stamp=datetime.now(), ab_type="DR", offercode=offercode_obj).save()
									raise CommandError("Customer attempts to reuse a code")
							else:
								receipt_msg = _("Redeem failed! %(offer_code)s does not belong to %(customer)s.") % {
									"offer_code":offer_code.code,
									"customer":offercode_obj.customer,
								}
								self.notify(su.phone, receipt_msg)
								raise CommandError("Customer attempts to redeem a code he doesnt own")
						except ObjectDoesNotExist:
							# Such phone number doesn't exist in customers' profiles, save it
							receipt_msg = _("%(phone)s is not in our record. %(offer_code)s offercode was not processed") % {
								"offer_code": offer_code.code,
								"phone": phone,
							}
							self.notify(su.phone, receipt_msg)
						except MultipleObjectsReturned, e:
							# Multiple customers registered with the same phone number, should be prevented
							print e
							
					except ObjectDoesNotExist:
						# The offer code is not found, or an invalid one
						receipt_msg = _("%(offer_code)s is not a valid offer code!") % {
							"offer_code": offer_code.code,
						}
						self.notify(su.phone, receipt_msg)
						OfferCodeAbnormal(time_stamp=datetime.now(), ab_type="IV", invalid_code=offer_code.code).save()
					except MultipleObjectsReturned, e:																	# Multiple offer codes found, which indicates a programming error
						print e

				# ------------------------OFFER : "offer<SPACE>description" ---------------
				elif parsed[0].lower() == OFFER:
					if len(parsed)<2:
						receipt_msg=_("Command Error! To start an offer, please use this command: offer<SPACE>offer_description")
						self.notify(su.phone,receipt_msg)
						raise CommandError("Incorrectly formed offer command: %s" % msg["text"])
					# This is an offer made by the merchant, not a redemption code

					description = ''.join([i+' ' for i in parsed[1:]]).strip()
					offer = Offer(merchant=su.merchant, title=description[:40],
							description=description, time_stamp=datetime.now(),
							starting_time=datetime.now())
					offer.save()
					offer.distribute()
					receipt_msg = _("We have received your offer message at %(time)s, %(number)d users have been reached. You can track the status of this offer: \"%(offer)s\" by typing \"status %(code)s\"") % {
						"time": pretty_datetime(offer.time_stamp),
						"offer": offer,
						"number": offer.num_received(),
						"code": offer.gen_tracking_code(),
					}
					self.notify(su.phone, receipt_msg)

				# --------------------- STATUS : "status<SPACE>trackingcode" ---------------
				elif parsed[0].lower() == STATUS:
					if (len(parsed)<2):
						receipt_msg=_("Command Error! To track an offer, please use this command: status<SPACE>trackingcode")
						self.notify(su.phone,receipt_msg)
						raise CommandError("Incorrectly formed status command: %s" % msg["text"])
					code = parsed[1].strip()
					
					try:
						trackingcode = TrackingCode.objects.get(code__iexact=code)
					except TrackingCode.DoesNotExist:
						receipt_msg = _("The tracking code can not be found. Please enter a correct tracking code.")
						self.notify(su.phone,receipt_msg)
						raise CommandError ("Tracking code not found")
					offer = trackingcode.offer
					people_sentto = offer.num_init_sentto
					people_forwarded = OfferCode.objects.filter(offer=trackingcode.offer,forwarder__isnull=False).count()
					receipt_msg = _("[%(code)s] This offer was sent to %(sentto)s customers and forwarded to %(forwarded)s other customers, totally %(total)d customers reached") % {
												"code":code,"sentto":people_sentto,
												"forwarded":people_forwarded,
												"total":int(people_sentto)+int(people_forwarded),
						}
					self.notify(su.phone,receipt_msg)
				# --------------------- RESIGNUP -------------------------
				elif parsed[0].lower() == MERCHANT_SIGNUP:
					receipt_msg = _("You are already a Shoppley merchant")
					self.notify(su.phone, receipt_msg)
		

				# --------------------- HELP: "help" -------------------------
				elif parsed[0].lower() == HELP:
					commands = self.merchant_help()
					self.notify(su.phone, commands)


				# --------------------- INCORRECT COMMAND: give them helps --------------
				else:
					receipt_msg=_("%s is not available. Here are the available commands:\n") % parsed[0]+ self.merchant_help()
					self.notify(su.phone,receipt_msg)

			#****************** COMMANDS FOR CUSTOMERS ********************************
			elif su and su.is_customer():
				text = msg["text"].strip()
				parsed = customer_pattern.parseString(text)
				phone = su.phone

				# ----------------- INFO : "info<SPACE>offercode+"----------------
				if parsed[0].lower() == INFO:
					if (len(parsed)<2):
						receipt_msg=_("Command Error! Please type 'info <SPACE> your offercode'.")
						self.notify(msg["from"],receipt_msg)
						raise CommandError('Incorrectly formed info command: "%s"' % msg["text"])

					customer_msg=""
					for i in parsed[1:]:
						parsed_offercode =i
						offercode = self.check_offercode(parsed_offercode,phone)			
						#print offercode		
						customer_msg = customer_msg+ self.info(offercode)
	
					self.notify(phone,customer_msg)
				# ------------------- STOP: "stop"----------------------
				elif parsed[0].lower() == STOP:
					
					if su.active:
						customer_msg = _("You chose to temporarily stop receiving offer messages. Please type START and send to 123456 to restart our service.")
						self.notify(phone,customer_msg)
						su.active = False
						su.save()

					else:
						customer_msg = _("You already elected to stop receiving offer messages. Please type START and send to 123456 to restart our service.")
						self.notify(phone,customer_msg)
				# ------------------- START: "start"-----------------------
				elif parsed[0].lower() == START :
					
					if not su.active:
						su.active = True
						su.save()
						customer_msg = _("Welcome back! You will start receiving offer messages again.")
						self.notify(phone, customer_msg)	
					else:
						customer_msg = _("You are active and receiving offer messages.")
						self.notify(phone, customer_msg)

				#-------------------- FORWARD: "forward<SPACE>offercode<SPACE>number+"---------------------
				elif parsed[0].lower() ==FORWARD:
					if (len(parsed) < 3):
						forwarder_msg='Fail to forward the offer! Please follow this command: "forward offercode" followed by one or more friends\' numbers'
						self.notify(su.phone,forwarder_msg)
						raise CommandError('Incorrectly formed forward command: "%s"' % msg["text"])
					ori_code = self.check_offercode(parsed[1],phone)
					ori_offer = ori_code.offer

					if (ori_code.customer!=su.customer):
						forwarder_msg= _("%s: Fail to forward! You are not the owner of this offercode.") % ori_code.code
						self.notify(phone,forwarder_msg)
						raise CommandError("Fail to forward! Customer attempts to forward an offercode he doesnt own")

					#f_state,created = ForwardState.objects.get_or_create(customer=su.customer,offer=ori_offer)
					parsed_numbers = [parse_phone_number(i) for i in parsed[2:]]
					#print "created:" , created
					#print "remaining:", f_state.remaining
					valid_receivers=set([ i for i in parsed_numbers if ori_offer.offercode_set.filter(customer__phone=i).count()==0 or Customer.objects.filter(phone=i).count()==0]) # those who havenot received the offer: new customers or customers who have not got the offer before
					invalid_receivers= set(parsed_numbers) - valid_receivers # those who have
					#allowed_forwards = f_state.allowed_forwards(len(valid_receivers))

					if len(valid_receivers)==0:
						forwarder_msg = _("[%s] All phone numbers you wanted to forward the code already received the offer.") % ori_code.code		
						self.notify(su.phone,forwarder_msg)
					
					else:
						forwarder_msg= _('[%s] was forwarded to ') % ori_code.code
						for r in valid_receivers:
							#f_state.update()
							friend_num = r
							friend_code, random_pw = ori_offer.gen_forward_offercode(ori_code,friend_num)	
							customer_msg = _("%(code)s: %(customer)s has forwarded you this offer:\n - merchant: %(merchant)s\n - expiration: %(expiration)s\n - description: %(description)s\n - deal: %(dollar_off)s off\n - address: %(address)s\nPlease use this code %(code)s to redeem the offer.\n")%{
									"customer":su,
									"merchant":ori_offer.merchant,
									"expiration":pretty_datetime(ori_code.expiration_time),
									"description":ori_offer.description,
									"dollar_off":ori_offer.dollar_off,
									"address":ori_offer.merchant.print_address(),
									"code":friend_code.code,
									}
							self.notify(friend_num,customer_msg)
							# the phone number is not one of our customers
							if random_pw:
								new_customer = friend_code.customer
								#print "created a customer for %s" % friend_num
								account_msg = _("Welcome to Shoppley! Here is your shoppley.com login info:\n - username: %(name)s\n - password: %(password)s")%{"name":new_customer.user.username,"password":random_pw,}
								self.notify(friend_num,account_msg)

						forwarder_msg= _('Offer by "%s" was forwarded to ') % ori_code.code
						forwarder_msg= forwarder_msg+ ''.join([str(i)+' ' for i in valid_receivers]) + "\nYou will receive points when they redeem." 
						#% f_state.remaining
						self.notify(su.phone,forwarder_msg)
				# --------------------- HELP: "help" -------------------------
				elif parsed[0].lower() == HELP:
					commands = self.customer_help()
					self.notify(su.phone, commands)
				# --------------------- RESIGNUP -------------------------
				elif parsed[0].lower() == SIGNUP:
					receipt_msg = _("You are already a Shoppley customer")
					self.notify(su.phone, receipt_msg)
				
				# ---------------------------- INCORRECT COMMAND : give them help -----------
				else:
					customer_msg=_("%s command is not available. Here is a list of accepted commands:\n") % parsed[0]+self.customer_help()
					self.notify(su.phone,customer_msg)

			else:
				# TODO: We should save all messages
				if not su:
					text = msg["text"].strip()
					phone= msg["from"]
					parsed = customer_pattern.parseString(text)
					
					#------------------------------- MERCHANT SIGNUP: "merchant_signup<SPACE>email<SPACE>zipcode<SPACE>business_name"-----------
					if  parsed[0].lower() ==MERCHANT_SIGNUP:
						if (len(parsed)<4):
							receipt_msg=_("Fail to sign up! Please follow this command: 'merchant_signup email zipcode business_name'")
							self.notify(phone,receipt_msg)      
							raise CommandError('Incorrectly formed merchant_signup command: "%s"' % msg["text"])

						parsed_email = parsed[1].lower()
						parsed_zip = parsed[2]

						business = ''.join(i+" " for i in parsed[3:]).strip()
						email = self.check_email(parsed_email,phone)
						zipcode= self.check_zipcode(parsed[2],phone)
				
						randompassword = gen_random_pw()
						new_user = User.objects.create_user(email,email,randompassword)
						EmailAddress.objects.add_email(new_user,email)
						zipcode_obj = ZipCode.objects.get(code=parsed_zip)
						clean_phone = parse_phone_number(phone,zipcode_obj.city.region.country.code)
						new_merchant = Merchant(user=new_user,phone = clean_phone,zipcode= zipcode_obj,
									business_name = business).save()


						receipt_msg = _("Sign up successfully! Please use these info to log in.\n username: %(email)s \n password: %(password)s") % {
							"email": email,
							"password": randompassword,
							}

						self.notify(phone,receipt_msg)	

					# ----------------------------------- SIGNUP: "signup<SPACE>email<SPACE>zipcode" ----------------
					elif parsed[0].lower() ==SIGNUP:
						if (len(parsed) <3):
							receipt_msg=_("Signup Error! Please follow this command: 'signup email zipcode'")
							self.notify(phone,receipt_msg)
							raise CommandError('Incorrectly formed signup command: "%s"' % msg["text"])

						parsed_email = parsed[1].lower()
						parsed_zip = parsed[2]	
						email = self.check_email(parsed_email,phone)
						zipcode= self.check_zipcode(parsed[2],phone)
						randompassword = gen_random_pw()
						receipt_msg = _("Sign up successfully! Please use these info to log in.\n username: %(email)s \n password: %(password)s") % {
							"email": email,
							"password": randompassword,
							}
						self.notify(phone,receipt_msg)
						new_user = User.objects.create_user(parsed_email,parsed_email,randompassword)
						EmailAddress.objects.add_email(new_user,parsed_email)
						zipcode_obj = ZipCode.objects.get(code=parsed_zip)
						clean_phone = parse_phone_number(phone,zipcode_obj.city.region.country.code)		
						new_customer = Customer(user=new_user,phone = clean_phone,zipcode= zipcode_obj).save()

					else:
					# -------------------------------- UNSUPPORTED NON-CUSTOMER COMMAND: ask them to sign up with us --------------
						receipt_msg=_("Welcome to Shoppley! You are currently not one of our users. Please sign up @ www.shoppley.com or send us a text message to 123456 with this command: \"signup<SPACE>email_address<SPACE>zipcode\" to sign up as a customer or \"merchant_signup<SPACE>email_address<SPACE>zipcode<SPACE>business_name\" to sign up as a business")
						print phone
						self.notify(phone,receipt_msg)

	def handle_noargs(self, **options):
		voice = Voice()
		voice.login()
		smses = voice.sms()
		#self.update_expired()

		for msg in extractsms(voice.sms.html):
			sms_notify(msg["from"], "hello")
			try:
				self.test_handle(msg)
			except CommandError:
				continue
		for message in voice.sms().messages:
			message.delete()
