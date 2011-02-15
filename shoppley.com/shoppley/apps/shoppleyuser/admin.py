from shoppleyuser.models import City, State, Category, ShoppleyUser
from shoppleyuser.models import Merchant, Customer, MerchantOfTheDay

from django.contrib import admin

admin.site.register(City)
admin.site.register(State)
admin.site.register(Category)
admin.site.register(ShoppleyUser)
admin.site.register(Merchant)
admin.site.register(MerchantOfTheDay)
admin.site.register(Customer)

