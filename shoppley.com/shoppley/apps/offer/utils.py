from shoppleyuser.models import ShoppleyUser
from django.conf import settings
import string, random
import uuid

MAX_CHARS = 160


def pretty_datetime(time):
	"""
	print %Y/%m/%d,%I:%M%p

	changed date separator to "/" since "-" makes
	it look like a number in smart phone txt message
	app, making it clickable [kwan]

	took out the year since it's obvious it's current year [kwan]
	"""
	return time.strftime("%m/%d %I:%M%p")
	#return time.strftime("%Y/%m/%d %I:%M%p")


def gen_tracking_code(chars=string.lowercase):
	return ''.join([random.choice(chars) for i in xrange(settings.TRACKING_CODE_LENGTH)])

### offer code only is only alphabetic
def gen_offer_code(chars=string.digits):
	#start = random.randint(0,28)
	#new_code = str(uuid.uuid4())[start:start+settings.OFFER_CODE_LENGTH]

	return ''.join([random.choice(chars) for i in xrange(settings.OFFER_CODE_LENGTH)])

def gen_random_pw():
	chars = string.letters + string.digits
	return ''.join([random.choice(chars) for i in xrange(settings.RANDOM_PASSWORD_LENGTH)])

def validateEmail(email):
	from django.core.validators import validate_email
	from django.core.exceptions import ValidationError
	try:
		validate_email( email )
		return True
	except ValidationError:
		return False

# cant handle irregular plurals for now
def pluralize(count,word):
	if count<=1:
		return str(count) + ' ' + word
	else:
		return str(count) + ' ' + word + 's'

def is_chars_over_max(string):
	return len(string)>160
import re, htmlentitydefs

##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.

def unescape(text):
	def fixup(m):
		text = m.group(0)
		if text[:2] == "&#":
            	# character reference
			try:
				if text[:3] == "&#x":
					return unichr(int(text[3:-1], 16))
				else:
					return unichr(int(text[2:-1]))
			except ValueError:
				pass
		else:
			# named entity
			try:
				text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
			except KeyError:
				pass
		return text # leave as is
	return re.sub("&#?\w+;", fixup, text)

from django.template import Context, Template

class TxtTemplates:
	templates = {
		"MERCHANT": {
			"REDEEM_PARAM_ERRORS": "Usage: #redeem <offer code> <customer phone>.  Command needs the offer code and the phone number of the customer.",
			"REDEEM_EXPIRED": "Sorry, offer \"{{ offer }}\" already expired.",
			"REDEEM_WRONG_MERCHANT": "Redeem Fail! \"{{ code }}\" was initiated by a different business, and not by you.",
			"REDEEM_SUCCESS": "{{ offer_code }} is a valid offer code! Redeemed by {{ customer }}.",
			"REDEEM_CODE_REUSE": "Code reuse! {{ offer_code }} was redeemed by {{ customer }} at {{ time }}.",
			"REDEEM_WRONG_CUSTOMER": "Redeem failed! {{ offer_code }} does not belong to {{ customer }}",
			"REDEEM_INVALID_CUSTOMER_NUM": "{{ phone }} is not in our record. {{ offer_code }} offercode was not processed",
			"REDEEM_INVALID_CODE": "{{ offer_code }} is not a valid offer code!",
			"ZIPCODE_COMMAND_ERROR": "Command Error! To change your zipcode, please reply with #zipcode new_zipcode",
			"ZIPCODE_CHANGE_SUCCESS": "{{ zipcode }} is your new zipcode. Your future offers will be distributed to customers in this new area.{{ number }} people in this area are signed up to receive offers. Tell your customers to sign up at Shoppley to receive last minute offers for free.",
			"BALANCE": "You have {{ points }} points.",
			"OFFER_COMMAND_ERROR": "Command Error! To start an offer, please use this command: #offer offer_description",
			"OFFER_NO_CUSTOMER" : "There were no customers that could be reached at this moment. Txt \"#status {{ code }}\" to track offer.",
		
			"OFFER_NOTENOUGH_BALANCE": "Your balance is {{ points }} points. At this time, you do not have enough points to reach customers.",
			"OFFER_SUCCESS": "We have received your offer at {{ time }}, {{ number }} users have been reached. Txt \"#status {{ code }}\" to track offer: {{ offer }}",
			"REOFFER_ZERO_CUSTOMER":"There were no new customers that could be reached at this moment. Txt #status {{ code }} to track this offer.",
			"REOFFER_SUCCESS": "{{ title }} was resent to {{ resentto }} new customers.",
			"REOFFER_NO_OFFER": "Failure to redistribute your offer! You have not started an offer yet. To start an offer, txt #offer description",
			"REOFFER_INVALID_TRACKING" : "The tracking code \"{{ code }}\" can not be found. Please re-enter a tracking code.",
			"REOFFER_WRONG_MERCHANT" : "Sorry offer with tracking code \"{{ code }}\" was not initiated by you. Please re-input your tracking code",
			"REOFFER_NOT_ALLOWED": "Sorry, you are not allowed to redistribute this offer, {{ offer }}, more than once.", 
			"STATUS_SUCCESS": "[{{ code }}] Offer: {{ offer }} [sent to {{ sentto }}], [forwarded to {{ forwarded }}], [redeemed by {{ redeemer }}]. Txt #status {{ code }} to track the offer",
			"STATUS_NO_OFFER": "Failure to get status! Offer has not yet been initiated. To start an offer, txt #offer description",
			"STATUS_INVALID_CODE": "The tracking code \"{{ code }}\" can not be found. Please re-enter a tracking code.",
			"STATUS_WRONG_MERCHANT" : "Sorry, offer by \"{{ code }}\" was not initiated by you. Please re-enter the tracking code",
			
			"RESIGNUP": "You are already a Shoppley merchant.",
			"HELP": "{{ help }}",
			"INCORRECT_COMMAND": "{{ command }} is not available. Available commands are:\n {{ help }}",
			"COMMAND_NOT_START_W_#": "{{ command }} is not a valid command. Our commands start with \"#\". Txt #help for all commands",
			"EXPIRE_INFO": "{{ offer }} expired [sent to {{ sentto }}] [forwarded {{ forwarded }}] [redeemed {{ redeem }}]"	,
			"HELP": "- #redeem offercode number: redeem a customer's offercode\n- #offer description: start an offer with its description.\n-#zip new_zipcode: change to a new zipcode (only support 02139 02142)- #status trackingcode: check the status of an offer you started\n- #balance: check point balance"	,
			"SIGNUP_COMMAND_ERROR":"Sign up error. To sign up, txt \"#merchant email zipcode business_name\""	,
			"SIGNUP_SUCCESS": "Sign up successful! Please use this info to log in. Username: {{ email }}, password: {{ password }}. Currently, {{ number }} people in your area are signed up to receive offers. Tell your customers to sign up at Shoppley to receive last minute offers for free."
		
		},
		"CUSTOMER": {
			"REDEEM_SUCCESS": "You have successfully redeemed your code at {{ merchant }}.",
			"BALANCE" : "You have {{ points }} points.",

			"OFFER_RECEIVED": "[{{ code }}] {{ title }} by {{ merchant }} (txt \"#info {{ code }}\" for address)",

			"REOFFER_EXTENSION": "[{{ code }}] {{ title }}, by {{ merchant }} at {{ address }}, is extended until {{ expiration }}",
			"REOFFER_NEWCUSTOMER_RECEIVED": "[{{ code }}] {{ title }} by {{ merchant }} (reply \"info {{ code }}\" for address)",

			"INFO_NO_OFFER" : "Offer not found. Offers have not been received yet.",
			"INFO" : "Redeem [{{ offercode }}] at {{ merchant }} \"{{ description }}\" [expires: {{ expiration }}]",
			"IWANT": "We have received your request: {{ request }}. Our dragons are hard at work finding the perfect deals for you.",
			"IWANT_COMMAND_ERROR": "Command Error! To request a deal, please reply with #iwant your_request",
			"STOP" : "You have elected to temporarily stop receiving offer messages. Please txt #start to {{ DEFAULT_SHOPPLEY }} to restart your service.",
			"RESTOP": "You already elected to stop receiving offer messages. Please txt #start to {{ DEFAULT_SHOPPLEY }} to restart your service."
,
			"START": "Welcome back! Dragons will re-start finding perfect deals for you.",
			"RESTART": "You are active and receiving offer messages.",
			"ZIPCODE_COMMAND_ERROR": "Command Error! To change your zipcode, please use this command: #zipcode new_zipcode",
			"ZIPCODE" : "{{ zipcode }} is your new zipcode. You will receive offers from this new area. There are {{ number }} stores signed up in this area. Tell your favorite stores to use Shoppley to send you any last minute offers for free.",
			"FORWARD_COMMAND_ERROR": "Failure to forward offer! Please txt \"#forward offercode(s)\" followed by one or more friends\' numbers separated by spaces",
			"FORWARD_WRONG_FORWARDER":"{{ code }}: Failure to forward! You are not the owner of this offercode." ,
			"FORWARD_ALL_RECEIVED": "[{{ code }}] All phone numbers that were forwarded the code, have already received the offer.",
			"FORWARD_SUCCESS": "Offer [{{ code }}] was forwarded to {{ numbers }}. You will receive points when it is redeemed.",
			"FORWARD_CUSTOMER_MSG": "{{ customer }} forwarded you an offer: {{ info }}. Use [{{ code }}] to redeem offer",
			"FORWARD_INFO":"{{ merchant }} \"{{ description }}\" [expires: {{ expires }}]",
			"FORWARD_NON_CUSTOMER_LOGIN": "Welcome to Shoppley! Here is your shoppley.com login info:\n - username: {{ name }}\n - password: {{ password }}" ,
			"RESIGNUP": "You are already a Shoppley customer",
			"INCORRECT_COMMAND": "{{ command }} command is not available. Available commands are:\n {{ help }}",
			"COMMAND_NOT_STARTED_W_#": "{{ command }} is not a valid command. Our commands start with \"#\". Txt #help for all commands",
			"HELP": "- #info offercode(s): lists information about offercode(s) separated by spaces\n- #forward offercode number(s): forward an offer to your friend(s) separated by spaces\n-#zip new_zipcode: change to a new zipcode (only support 02139 02142)\n-#stop: stop receiving messages from us\n- #start: restart receiving messages from us\n- #help: list available commands\n- #balance: check point balance",
			"SIGNUP_COMMAND_ERROR": "Signup Error! To signup, please txt \"#signup email zipcode\"",
			"SIGNUP_SUCCESS": "Sign up successful! Please use this info to log in. Username: {{ email }}; password: {{ password }}. Currently,{{ number }} stores are signed up in your area. Tell your favorite stores to use Shoppley to send you any last minute offers for free.",
			  

		},
		"SHARED": {
			"INVALID_EMAIL": "\"{{ email }}\" is not a valid email address. Please provide a new and valid email.",
			"INVALID_NUMBER": "\"{{ number }}\" is not a valid phone number. Please provide a new and valid phone number without spaces.",
			"EMAIL_TAKEN": "\"{{ email }}\" is already registered with shoppley. Please provide another email.",
			"PHONE_TAKEN": "\"{{ phone }}\" is already registered with shoppley. You can now use our services.",
			"OFFERCODE_NOT_EXIST": "Offercode {{ code }} does not exist.",
			"INVALID_ZIPCODE": "Zipcode {{ zipcode }} does not exist. Please re-enter a zipcode.",
			"NON_USER": "Welcome to Shoppley! To sign up, visit shoppley @ {{ site }} or send a text message to {{ shoppley_num }} with this command: \"#signup email zipcode\" to sign up as a customer OR \"merchant email zipcode business_name\" to sign up as a business"
		}
	}

	def render(self,tstring,c):
		t=Template(tstring)
		return unescape(t.render(Context(c)))
