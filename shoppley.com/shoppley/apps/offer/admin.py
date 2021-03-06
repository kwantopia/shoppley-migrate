from offer.models import Offer, OfferCode, Transaction, BlackListWord, BlackListOffer, TrackingCode
from django.contrib import admin
import logicaldelete.admin


class OfferAdmin(logicaldelete.admin.ModelAdmin):
  list_filter = ['time_stamp'] 

class BlackListWordAdmin(logicaldelete.admin.ModelAdmin):
  list_filter = ['date_modified'] 

class BlackListOfferAdmin(logicaldelete.admin.ModelAdmin):
  list_filter = ['date_modified'] 

admin.site.register(Offer, OfferAdmin)
admin.site.register(OfferCode)
admin.site.register(TrackingCode)
admin.site.register(Transaction)
admin.site.register(BlackListWord, BlackListWordAdmin)
admin.site.register(BlackListOffer, BlackListOfferAdmin)
