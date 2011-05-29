from shoppleyuser.models import ShoppleyUser
from django.conf import settings
import string, random
import uuid


def gen_offer_code(chars=string.letters+string.digits):
	#start = random.randint(0,28)
	#new_code = str(uuid.uuid4())[start:start+settings.OFFER_CODE_LENGTH]
	return ''.join([random.choice(chars) for i in xrange(settings.OFFER_CODE_LENGTH)])

def validateEmail(email):
	from django.core.validators import validate_email
	from django.core.exceptions import ValidationError
	try:
		validate_email( email )
		return True
	except ValidationError:
		return False


