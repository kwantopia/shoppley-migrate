from shoppleyuser.models import ShoppleyUser
from django.conf import settings
import string, random
import uuid

MAX_CHARS = 160


def pretty_datetime(time):
	"""
	print %Y-%m-%d,%I:%M%p
	"""
	return time.strftime("%Y-%m-%d,%I:%M%p")

def gen_offer_code(chars=string.lowercase+string.digits):
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

