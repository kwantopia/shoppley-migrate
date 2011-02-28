from django.conf import settings
import string, random
import uuid


def gen_offer_code(chars=string.letters+string.digits):
	#start = random.randint(0,28)
	#new_code = str(uuid.uuid4())[start:start+settings.OFFER_CODE_LENGTH]
	return ''.join([random.choice(chars) for i in range(settings.OFFER_CODE_LENGTH)])

