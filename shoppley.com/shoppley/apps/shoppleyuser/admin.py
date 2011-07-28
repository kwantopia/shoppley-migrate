from shoppleyuser.models import City, Region, Category, ShoppleyUser, Country
from shoppleyuser.models import Merchant, Customer, MerchantOfTheDay, ZipCode
from shoppleyuser.models import Location, IWantRequest
from django.contrib import admin

class MerchantAdmin(admin.ModelAdmin):
	list_display = ('business_name', 'admin', 'merchant_email', 'phone', 'address_1', 'zipcode','latlon')
	#list_filter = ('zipcode',)
	search_fields = ('business_name', 'admin', 'user__email', 'zipcode__code')

	def merchant_email(self, obj):
		return obj.user.email 
	def latlon(self,obj):
                return "" +str(obj.location.location.x) + ";" + str(obj.location.location.y)

	merchant_email.short_description = 'E-mail'
admin.site.register(Location)
class CustomerAdmin(admin.ModelAdmin):
	list_display = ('username','customer_email', 'phone', 'address_1', 'zip','latlon')
	search_field = ('user__email', 'zipcode__code')
	def customer_email(self, obj):
		return obj.user.email
	def username(self, obj):
		return obj.user.username
	def zip(self,obj):
		if obj.zipcode:
			return obj.zipcode.code
		else:
			return "null"
	def latlon(self,obj):
		return "" +str(obj.location.location.x) + ";" + str(obj.location.location.y)
	customer_email.short_description = 'E-mail'

admin.site.register(Country)
admin.site.register(City)
admin.site.register(Region)
admin.site.register(Category)
admin.site.register(ZipCode)
admin.site.register(ShoppleyUser)
admin.site.register(IWantRequest)
admin.site.register(Merchant, MerchantAdmin)
admin.site.register(MerchantOfTheDay)
admin.site.register(Customer, CustomerAdmin)

