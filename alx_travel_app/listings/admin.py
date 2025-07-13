from django.contrib import admin
from .models import Booking, Listing, Payment


admin.site.register(Booking)
admin.site.register(Listing)
admin.site.register(Payment)