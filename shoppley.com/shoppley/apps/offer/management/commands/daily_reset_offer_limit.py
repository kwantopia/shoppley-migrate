from django.core.management.base import NoArgsCommand,CommandError
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext, string_concat
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.conf import settings
from django.contrib.auth.models import User

from shoppleyuser.models import Customer

class Command(NoArgsCommand):
	def handle_noargs(self, **options):
		for c in Customer.objects.all():
			print "reset", c, " 's offer count to", c.offer_count
			c.daily_reset()
