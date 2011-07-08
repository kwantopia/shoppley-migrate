from shoppleyuser.models import City, Region, Category, ShoppleyUser, Country
from shoppleyuser.models import Merchant, Customer, MerchantOfTheDay, ZipCode
from shoppleyuser.models import Location
from django.contrib import admin

class MerchantAdmin(admin.ModelAdmin):
	list_display = ('business_name', 'admin', 'merchant_email', 'phone', 'address_1', 'zipcode')
	#list_filter = ('zipcode',)
	search_fields = ('business_name', 'admin', 'user__email', 'zipcode__code')

	def merchant_email(self, obj):
		return obj.user.email 
	merchant_email.short_description = 'E-mail'
admin.site.register(Location)
admin.site.register(Country)
admin.site.register(City)
admin.site.register(Region)
admin.site.register(Category)
admin.site.register(ZipCode)
admin.site.register(ShoppleyUser)
admin.site.register(Merchant, MerchantAdmin)
admin.site.register(MerchantOfTheDay)
admin.site.register(Customer)

