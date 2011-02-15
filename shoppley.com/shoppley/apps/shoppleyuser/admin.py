from shoppleyuser.models import City, Region, Category, ShoppleyUser, Country
from shoppleyuser.models import Merchant, Customer, MerchantOfTheDay, ZipCode

from django.contrib import admin

admin.site.register(Country)
admin.site.register(City)
admin.site.register(Region)
admin.site.register(Category)
admin.site.register(ZipCode)
admin.site.register(ShoppleyUser)
admin.site.register(Merchant)
admin.site.register(MerchantOfTheDay)
admin.site.register(Customer)

