from django.conf import settings
import string, random

def gen_offer_code(chars=string.letters+string.digits):
	return ''.join([random.choice(chars) for i in range(settings.OFFER_CODE_LENGTH)])

