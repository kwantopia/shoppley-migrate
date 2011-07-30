from django.contrib.auth import  login, logout
from django.contrib.auth.models import User
from emailconfirmation.models import EmailAddress
from shoppleyuser.models import ShoppleyUser

class ShoppleyBackend:

	supports_object_permissions = False
	supports_anonymous_user = True
	supports_inactive_user = True

	def authenticate(self, username=None, password=None):
		user = None
		username = username.strip()
		try:
			user = User.objects.get(username=username)
					
		except User.DoesNotExist:
			shoppleys = ShoppleyUser.objects.filter(phone=username)
			if shoppleys.count()>0:
				su = shoppleys[0]
				try:
					user = User.objects.get(username = su.user.username)
				except User.DoesNotExist:
					pass
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
			user.check_password(user)
			
			print "user:" , user
			return user
		return None


	def get_user(self, user_id):
		try:
			return User.objects.get(pk=user_id)
		except User.DoesNotExist:
			return None
