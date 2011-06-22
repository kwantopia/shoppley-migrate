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
	"""
	return time.strftime("%Y/%m/%d %I:%M%p")


def gen_tracking_code(chars=string.digits):
	return ''.join([random.choice(chars) for i in xrange(settings.TRACKING_CODE_LENGTH)])

### offer code only is only alphabetic
def gen_offer_code(chars=string.lowercase):
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
			"REDEEM_WRONG_MERCHANT": "Redeem Fail! {{ code }} was initiated by a different business, and not by you.",
			"REDEEM_SUCCESS": "{{ offer_code }} is a valid offer code! Redeemed by {{ customer }}.",
			"REDEEM_CODE_REUSE": "Code reuse! {{ offer_code }} was redeemed by {{ customer }} at {{ time }}.",
			"REDEEM_WRONG_CUSTOMER": "Redeem failed! {{ offer_code }} does not belong to {{ customer }}",
			"REDEEM_INVALID_CUSTOMER_NUM": "{{ phone }} is not in our record. {{ offer_code }} offercode was not processed",
			"REDEEM_INVALID_CODE": "{{ offer_code }} is not a valid offer code!",
			"ZIPCODE_COMMAND_ERROR": "Command Error! To change your zipcode, please reply with #zipcode new_zipcode",
			"ZIPCODE_CHANGE_SUCCESS": "{{ zipcode }} is your new zipcode. Your later offers will be distributed to customers in this new area.",
			"BALANCE": "You have {{ points }} points.",
			"OFFER_COMMAND_ERROR": "Command Error! To start an offer, please use this command: #offer offer_description",
			"OFFER_NO_CUSTOMER" : "There were no customers that could be reached at this moment. Txt #status {{ code }} to track this offer.",
		
			"OFFER_NOTENOUGH_BALANCE": "Your balance is {{ points }} points. You do not have enough to reach customers. Please try again when you have enough in your balance.",
			"OFFER_SUCCESS": "We have received your offer at {{ time }}, {{ number }} users have been reached. Txt #status {{ code }} to track this offer: {{ offer }}",
			"REOFFER_ZERO_CUSTOMER":"There were no new customers that could be reached at this moment. Txt #status %s to track this offer.",
			"REOFFER_SUCCESS": "{{ title }} was resent to {{ resentto }} new customers.",
			"REOFFER_NO_OFFER": "Fail to redistribute your offer! You have not started an offer yet. To start an offer, txt #offer description",
			"REOFFER_INVALID_TRACKING" : "The tracking code {{ code }} can not be found. Please enter a correct tracking code.",
			"REOFFER_WRONG_MERCHANT" : "Sorry offer with tracking code {{ code }} was not started by you. Please input your correct tracking code",
			"REOFFER_NOT_ALLOWED": "Sorry, you are allowed to redistribute the offer, {{ offer }}, more than once.", 
			"STATUS_SUCCESS": "[{{ code }}] Offer: {{ offer }} [sent to {{ sentto }}], [forwarded to {{ forwarded }}], [redeemed by {{ redeemer }} Txt #status {{ code }} to track the offer",
			"STATUS_NO_OFFER": "Fail to get status! You have not started an offer yet. To start an offer, txt #offer description",
			"STATUS_INVALID_CODE": "The tracking code {{ code }} can not be found. Please enter a correct tracking code.",
			"STATUS_WRONG_MERCHANT" : "Sorry, offer by {{ code }} was not started by you. Please txt again with your correct tracking code",
			
			"RESIGNUP": "You are already a Shoppley merchant.",
			"HELP": "{{ help }}",
			"INCORRECT_COMMAND": "{{ command }} is not available. Here are the available commands:\n {{ help }}",
			"COMMAND_NOT_START_W_#": "{{ command }} is not a valid command. Our commands start with \"#\". Txt #help for all commands",
			"EXPIRE_INFO": "{{ offer }} expired [sent to {{ sentto }}] [forwarded {{ forwarded }}] [redeemed {{ redeem }}]"	,
			"HELP": "- #redeem offercode number: redeem a customer's offercode\n- #offer description: start an offer with its description.\n-#zip new_zipcode: change to a new zipcode (only support 02139 02142)- #status trackingcode: check the status of an offer you started\n- #balance: check point balance"	,
			"SIGNUP_COMMAND_ERROR":"Fail to sign up! To sign up, txt \"#merchant email zipcode business_name\""	,
			"SIGNUP_SUCCESS": "Sign up successfully! Please use these info to log in. Username: {{ email }}, password: {{ password }}"
		
		},
		"CUSTOMER": {
			"REDEEM_SUCCESS": "You have successfully redeemed your code at {{ merchant }}.",
			"BALANCE" : "You have {{ points }} points.",

			"OFFER_RECEIVED": "[{{ code }}] {{ title }} by {{ merchant }} (txt \"#info {{ code }}\" for address)",

			"REOFFER_EXTENSION": "[{{ code }}] {{ title }}, by {{ merchant }} at {{ address }}, is extended until {{ expiration }}",
			"REOFFER_NEWCUSTOMER_RECEIVED": "[{{ code }}] {{ title }} by {{ merchant }} (reply \"info {{ code }}\" for address)",

			"INFO_NO_OFFER" : "Fail to find your offer! You have not received any offer yet.",
			"INFO" : "Redeem [{{ offercode }}] at {{ merchant }} \"{{ description }}\" [expires: {{ expiration }}]",
			"IWANT": "We have received your request: {{ request }}. Our search monkeys are hard at work finding the perfect deals for you.",
			"IWANT_COMMAND_ERROR": "Command Error! To request for a deal, please reply with #iwant your_request",
			"STOP" : "You chose to temporarily stop receiving offer messages. Please txt #start to {{ DEFAULT_SHOPPLEY }} to restart your service.",
			"RESTOP": "You already elected to stop receiving offer messages. Please txt #start to {{ DEFAULT_SHOPPLEY }} to restart your service."
,
			"START": "Welcome back! You will start receiving offer messages again.",
			"RESTART": "You are active and receiving offer messages.",
			"ZIPCODE_COMMAND_ERROR": "Command Error! To change your zipcode, please use this command: #zipcode new_zipcode",
			"ZIPCODE" : "{{ zipcode }} is your new zipcode. You will receive offers from this new area.",
			"FORWARD_COMMAND_ERROR": "Fail to forward the offer! Please txt \"#forward offercode(s)\" followed by one or more friends\' numbers separated by spaces",
			"FORWARD_WRONG_FORWARDER":"{{ code }}: Fail to forward! You are not the owner of this offercode." ,
			"FORWARD_ALL_RECEIVED": "[{{ code }}] All phone numbers you wanted to forward the code to already received the offer.",
			"FORWARD_SUCCESS": "Offer [{{ code }}] was forwarded to {{ numbers }}. You will receive points when they redeem.",
			"FORWARD_CUSTOMER_MSG": "{{ customer }} forwarded you an offer: {{ info }}. Use [{{ code }}] to redeem",
			"FORWARD_INFO":"{{ merchant }} \"{{ description }}\" [expires: {{ expires }}]",
			"FORWARD_NON_CUSTOMER_LOGIN": "Welcome to Shoppley! Here is your shoppley.com login info:\n - username: {{ name }}\n - password: {{ password }}" ,
			"RESIGNUP": "You are already a Shoppley customer",
			"INCORRECT_COMMAND": "{{ command }} command is not available. Here is a list of available commands:\n {{ help }}",
			"COMMAND_NOT_STARTED_W_#": "{{ command }} is not a valid command. Our commands start with \"#\". Txt #help for all commands",
			"HELP": "- #info offercode(s): list information about an offercode or offercodes separated by spaces\n- #forward offercode number(s): forward an offer to your friend(s) separated by spaces\n-#zip new_zipcode: change to a new zipcode (only support 02139 02142)\n-#stop: stop receiving messages from us\n- #start: restart receiving messages from us\n- #help: list available commands\n- #balance: check point balance",
			"SIGNUP_COMMAND_ERROR": "Signup Error! To signup, please txt \"#signup email zipcode\"",
			"SIGNUP_SUCCESS": "Sign up successful! Please use this info to log in. Username: {{ email }}; password: {{ password }}",
			  

		},
		"SHARED": {
			"INVALID_EMAIL": "\"{{ email }}\" is not a valid email address. Please provide a new and valid email.",
			"EMAIL_TAKEN": "\"{{ email }}\" is already registered with shoppley. Please provide another email.",
			"PHONE_TAKEN": "\"{{ phone }}\" is already registered with us. You can now use our services.",
			"OFFERCODE_NOT_EXIST": "Offercode {{ code }} does not exist.",
			"INVALID_ZIPCODE": "Zipcode {{ zipcode }} does not exist. Please provide a correct zipcode.",
			"NON_USER": "Welcome to Shoppley! You are currently not one of our users. Please sign up @ {{ site }} or send us a text message to {{ shoppley_num }} with this command: \"#signup email zipcode\" to sign up as a customer or \"merchant email zipcode business_name\" to sign up as a business"
		}
	}

	def render(self,tstring,c):
		t=Template(tstring)
		return unescape(t.render(Context(c)))
