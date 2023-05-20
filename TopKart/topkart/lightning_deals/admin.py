from django.contrib import admin
from .models import LightningDeal,Order,CustomUser

# Register your models here.
admin.site.register(Order)
admin.site.register(LightningDeal)
admin.site.register(CustomUser)




