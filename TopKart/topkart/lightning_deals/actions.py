from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from .common import *
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import LightningDeal,Order
from .views import LightningDealHandler,OrderHandler


@attach_user_to_request
@user_passes_test(lambda u: u.groups.filter(name='admin').exists())
def create_update_lightning_deal(request):
    # Checking the request method
    if request.method == 'POST':

        #Creating the lighting deal through class LightningDealHandler based on request
        return LightningDealHandler.create_lightning_deal(request)
    elif request.method == 'PUT':

        # Checkung the payload
        if not request.PUT['deal_id']:
            return JsonResponse({'error': 'Lightning deal ID is required to update the deal'},status=400)
        else:
            deal_id = request.PUT['deal_id']

            #Updating the lighting deal through class LightningDealHandler based on request
            return LightningDealHandler.update_lightning_deal(request,deal_id)

        return JsonResponse({'message': 'Lightning deal created successfully'},status=200)
    else:
        return JsonResponse({'message': 'Method not allowed'}, status=405)


@csrf_exempt
@attach_user_to_request
@user_passes_test(lambda u: u.groups.filter(name='admin').exists())
def update_order_status(request):
    #updates the order status
    if request.method == 'PUT':
        # Checking the payload
        if not request.PUT['order_id']:
            return JsonResponse({'error': 'Order ID is required to update the approve the order'},status=400)
        else:
            order_id = request.PUT['order_id']
            #Updating the order through class OrderHandler
            return OrderHandler.update_order(request,request.PUT['order_id'])
    else:
        return JsonResponse({'message': 'Method not allowed'}, status=405)


@csrf_exempt
@attach_user_to_request
@user_passes_test(lambda u: u.groups.filter(name='customer').exists())
def get_unexpired_deals(request):
    if request.method == 'GET':
        # Getting all the active lightning deals
        return LightningDealHandler.get_lightning_deals(request)
    else:
        return JsonResponse({'message': 'Method not allowed'}, status=405)


@csrf_exempt
@attach_user_to_request
@user_passes_test(lambda u: u.groups.filter(name='customer').exists())
def place_order(request):
    if request.method == 'POST':
        lightning_deal_id = request.POST.get('lightning_deal_id')

        # Validating the payload
        if not lightning_deal_id:
            return JsonResponse({'message': 'Lightning deal not found'}, status=404)

        # Creating a new order
        return OrderHandler.create_order(request,request.user.username,lightning_deal_id)
        
    else:
        return JsonResponse({'message': 'Method not allowed'}, status=405)

@csrf_exempt
@attach_user_to_request
@user_passes_test(lambda u: u.groups.filter(name='customer').exists())
def check_order_status(request):
    if request.method == 'GET':
        order_id = request.GET.get('order_id')
        if not order_id:
            return JsonResponse({'message': 'Order not found'}, status=404)
        else:
            return OrderHandler.get_order(request,order_id)
    else:
        return JsonResponse({'message': 'Method not allowed'}, status=405)

@csrf_exempt
@attach_user_to_request
@user_passes_test(lambda u: u.groups.filter(name='admin').exists())
def get_expired_lightning_deals(request):
    # Getting the current time
    current_time = datetime.utcnow()

    # Querying the expired lightning deals
    expired_deals = LightningDeal.objects.filter(expiry_time__lt=current_time)

    # Preparing the response data
    expired_deals = []
    for deal in expired_deals:
        serialized_deal = {
            'id': deal.id,
            'product_name': deal.product_name,
            'expiry_time': deal.expiry_time.isoformat(),
            'deal_code':deal.deal_code,
            'final_price':deal.final_price,
            'actual_price':deal.actual_price,
            'created_on':deal.created_on
        }
        expired_deals.append(expired_deal)

    return JsonResponse({'expired_deals': expired_deals},status=200)