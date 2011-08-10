from django.contrib.auth import  login, logout
from django.contrib.auth.models import User
from emailconfirmation.models import EmailAddress
from shoppleyuser.models import ShoppleyUser,  ShoppleyPhone

class ShoppleyBackend(object):

	supports_object_permissions = False
	supports_anonymous_user = True
	supports_inactive_user = True

	def authenticate(self, username=None, password=None):
		user = None
		username = username.strip()
		try:
			user = User.objects.get(username=username)
					
		except User.DoesNotExist:
			if ShoppleyPhone.objects.filter(number = username).exists():
				p = ShoppleyPhone.objects.filter(number = username)[0]
				if p.is_customerphone():
					p = p.customerphone
					user = p.customer.user
				else:
					p = p.merchantphone
					user = p.merchant.user
			else:
				emails = EmailAddress.objects.filter(email= username)
				print "email:", username
				print "emails:", emails
				if emails.count()>0:
					try:
						user = User.objects.get(username=emails[0].user.username)
			
					except User.DoesNotExist:
						pass
		if user:
			try:
				su = user.shoppleyuser
				if su.is_fb_connected:#fb connected user cant login with this backend
					return None
			except ShoppleyUser.DoesNotExist:
				pass
			if user.check_password(password):

			
		#		print "user:" , user
				return user
		return None


	def get_user(self, user_id):
		try:
			return User.objects.get(pk=user_id)
		except User.DoesNotExist:
			return None
