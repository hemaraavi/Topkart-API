from django.urls import path
from .views import *
from .actions import *

urlpatterns = [
    # Allows you to create user where user type is required
    path(r'create/users/',CreateUserWithPermissions.as_view()),

    # Allows admin to  create or upadate deals
    path(r'create/update/deals/', create_update_lightning_deal),

    # Allows admin to  change order status
    path(r'update/order_status/', update_order_status),

    # Allows customer to create order
    path(r'place/order/', place_order),

    #Allows customer to check order status
    path(r'check/order_status/', check_order_status),

    # Returns all active deals
    path(r'get/active/deals/', get_unexpired_deals),

    # Return all inactive deals
    path(r'get/expired/deals/', get_expired_lightning_deals),   
]