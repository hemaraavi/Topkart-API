from .models import *
from functools import wraps
from django.http import JsonResponse

def attach_user_to_request(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.method == 'POST':
            username = request.POST.get('username')
        else:
            username = request.GET.get('username')

        try:
            user = CustomUser.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        request.user = user

        return func(request, *args, **kwargs)

    return wrapper