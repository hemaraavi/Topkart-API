from django.shortcuts import render,get_object_or_404
from django.http import JsonResponse 
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
from django.contrib.auth.models import User, Permission, Group
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, timedelta
from .models import *
import json
import random 


class CreateUserWithPermissions(ListView):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        # Defining permission dict based on User Type
        self.user_based_perms = {'admin'    : ['can_approve_order','can_view_order','can_edit_order'],
                                 'customer' : ['can_create_order','can_view_order']
                                 }

    def post(self, request,*args, **kwargs):
        request_data = json.loads(request.body)
        username = request_data.get('username')
        password = request_data.get('password')
        email = request_data.get('email')
        phone_number = request_data.get('phone')
        user_type = request_data.get('user_type')

        # Validating User Type from request
        if not user_type :
            error = {'error':'User Type is required'}
            return JsonResponse(error,status=400)

        elif user_type.lower() not in self.user_based_perms:
            error = {'error':'User Type is Invalid'}
            return JsonResponse(error,status=400)

        else:
            # Get user specific permissions
            user_based_permissions = self.user_based_perms.get(user_type,[])

        # Creating user
        error,created_user = self.create_user(username,password,email,phone=phone_number)
        if error or not created_user:
            return JsonResponse(error, status=400)
        else:
            # Creating
            user_role = create_role_with_permissions(user_type.lower(),user_based_permissions)
            if not user_role:
                error = {'error':'Fail'}
                return JsonResponse({'message': 'Fail'}, status=500)
            else:
                # Assigning the role to user
                created_user.groups.add(user_role)

        return JsonResponse({'message': 'Sucess'}, status=200)
        

    def create_user(self,username,password,email,phone=''):
        if username and password and email:
            # Get or Create a new user
            user,created = CustomUser.objects.get_or_create(username=username,password=password,
                                                    email=email,phone_number=phone)
            if not created:
                error = {'error': 'User already exists'}
                creation_status = created
            else:
                error = {}
                creation_status = user
        else:
            error = {'error': 'Username,Password and Email are required.'}
            creation_status = False
        return error,creation_status


def create_role_with_permissions(name,permissions):
    # Name and Permissions are required to create a Role
    if not name or  not permissions:
        return False

    # Create or Get a  role
    role , created = Group.objects.get_or_create(name=name)

    # Getting permissions
    permission_objects = Permission.objects.filter(codename__in = permissions)

    # Assigning them to assign to a specific Role
    for each_permission in permission_objects:
        role.permissions.add(each_permission)
    return role



class LightningDealHandler:
    @staticmethod
    def create_lightning_deal(request):
        # Get the necessary data from the request
        product_name =  request.POST.get('product_name')
        actual_price =  request.POST.get('actual_price')
        final_price  =  request.POST.get('final_price')
        total_units  =  request.POST.get('total_units')
        available_units = request.POST.get('available_units')
        active_hours =  request.POST.get('active_hours')
        
        if not active_hours:
            # Calculate the expiry time for the lightning deal (12 hours from now)
            expiry_time = datetime.utcnow() + timedelta(hours=12)

        elif active_hours >12:
            error = {
                'error': 'Lightning Deal Expiry Time is more than 12 Hours'
            }
            return JsonResponse(error,status=400)

        else:
            # Calculate the expiry time for the lightning deal based on active hours
            expiry_time = datetime.utcnow() + timedelta(hours=active_hours)

        # Generating Deal code for the lightning Deal
        deal_code = generate_deal_code(product_name,int(final_price))

        # Creating the lightning deal instance
        lightning_deal = LightningDeal(
            product_name=product_name,
            deal_code=deal_code,
            actual_price=actual_price,
            final_price=final_price,
            total_units=total_units,
            available_units=available_units,
            expiry_time=expiry_time,
            is_active=True
        )
        lightning_deal.save()

        # Returning a success response
        return JsonResponse({'message':"Lightning Deal created Sucessfully"},status=200)

    @staticmethod
    def get_lightning_deals(request):
        is_active = request.GET.get('is_active', True)
        deal_code = request.GET.get('deal_code','')
        product_name = request.GET.get('product_name','')
        final_price = request.GET.get('final_price','')

        #Framing filters to get deal
        filters = {'is_active':is_active}
        if deal_code:
            filter['deal_code'] = deal_code
        if product_name:
            filter['product_name'] = product_name
        if final_price:
            filter['final_price'] = final_price

        # Retrieving the lightning deal from the database
        lightning_deals = list(LightningDeal.objects.filter(**filters).values(
            'deal_code','product_name','actual_price','id',
            'final_price','total_units','available_units'
        ))

        # Returning the lightning deal details in the response
        response_data = {
            'data' : lightning_deals
        }
        return JsonResponse(response_data,status=200)

    @staticmethod
    def update_lightning_deal(request, lightning_deal_id):
        # Retrieving the lightning deal from the database
        lightning_deal = get_object_or_404(LightningDeal, pk=lightning_deal_id)

        # Updating the necessary fields based on the request data
        if 'product_name' in request.PUT:
            lightning_deal.product_name = request.get['product_name']
        if 'actual_price' in request.PUT:
            lightning_deal.actual_price = float(request.get['actual_price'])
        if 'final_price' in request.PUT:
            lightning_deal.final_price = float(request.get['final_price'])
        if 'total_units' in request.PUT:
            lightning_deal.total_units = int(request.get['total_units'])
        if 'is_active' in request.PUT:
            lightning_deal.is_active = int(request.get['is_active'])
        
        # Saving the updated lightning deal
        lightning_deal.save()

        # Returning a success response
        response_data = {
            'message': 'Lightning deal updated successfully.'
        }
        return JsonResponse(response_data,status=200)

def generate_deal_code(product_name, final_price):
    # Generating a random number between 1 and 9999
    random_number = random.randint(1, 9999)

    # Concatenating the product name, final price, and random number
    deal_code = f"{product_name}{final_price}{random_number}"

    return deal_code
    


class OrderHandler:
    @staticmethod
    def create_order(request, customer_name,lightning_deal_id):
        # Retrieving the lightning deal associated with the order
        lightning_deal = get_object_or_404(LightningDeal, pk=lightning_deal_id)

        if not lightning_deal.is_active:
            response_data = {
            'message': 'Cannot Place Order for Expired Deal.'
        }
            return JsonResponse(response_data,status=400)
        #Get the customer who place the order
        customer = get_object_or_404(CustomUser, username=customer_name)
        order_reference = generate_order_code(lightning_deal.product_name,customer.username)
        # Creating the order instance
        order = Order(
            lightning_deal=lightning_deal,
            customer= customer,
            order_reference=order_reference,
            status = 'OPEN'
        )
        order.save()

        # Returning a success response
        response_data = {
            'message': 'Order Placed successfully.',
            'order_id':order.id
        }
        return JsonResponse(response_data,status=200)

    @staticmethod
    def get_order(request, order_id):
        # Retrieving the order object based on the order ID
        order =  get_object_or_404(Order, pk=order_id)

        # Preparing the order information
        order_data = {
            'order_id': order.id,
            'customer_id': order.customer.id,
            'customer_name':order.customer.username,
            'order_reference':order.order_reference,
            'lightning_deal_id': order.lightning_deal.id,
            'product_name':order.lightning_deal.product_name,
            'status': order.status,
        }

        return JsonResponse({'order': order_data},status=200)
    

    @staticmethod
    def update_order(request, order_id):
        # Retrieving the order from the database
        order = get_object_or_404(Order, pk=order_id)

        order_status = Order._meta.get_field('status').choices

        # Updating the necessary fields based on the request data
        if 'status' in request:
            if request.PUT.get['status'] not in order_status:
                response_data = {
                    'message': 'Selected Status does not exist'
                }
                return JsonResponse(response_data,status=400)
            else:
                order.status = request.POST['status']

        # Saving the updated order
        order.save()

        # Returning a success response
        response_data = {
            'message': 'Order updated successfully.'
        }
        return JsonResponse(response_data,status=200)

    @staticmethod
    def delete_order(request, order_id):
        # Retrieving the order from the database
        order = get_object_or_404(Order, pk=order_id)

        # Deleting  the order
        order.delete()

        # Returning a success response
        response_data = {
            'message': 'Order deleted successfully.'
        }
        return JsonResponse(response_data)

def generate_order_code(product_name, customer_name):
    # Generating a random number between 1 and 9999
    random_number = random.randint(1, 9999)

    # Concatenating the product name, final price, and random number
    order_code = f"{product_name}{customer_name}{random_number}"

    return order_code
