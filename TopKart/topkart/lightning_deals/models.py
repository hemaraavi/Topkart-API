from django.db import models
from django.contrib.auth.models import Permission,AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    username = models.CharField(max_length=120,unique=True,null=False)
    email = models.EmailField(unique=True,blank=False, null=False)
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.username

class LightningDeal(models.Model):
    id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=128)
    deal_code = models.CharField(max_length=50,unique=True)
    actual_price = models.FloatField(default=0)
    final_price = models.FloatField(default=0)
    total_units = models.PositiveIntegerField(default=0)
    available_units = models.PositiveIntegerField(default=0)
    expiry_time = models.DateTimeField()
    is_active = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product_name', 'deal_code')
    
    def __str__(self):
        return self.product_name

class Order(models.Model):
    id = models.AutoField(primary_key=True)
    order_reference = models.CharField(max_length=50,default='')
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    lightning_deal = models.ForeignKey(LightningDeal, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('OPEN','Open'),
        ('APPROVED', 'Approved'),
        ('CANCELLED', 'Cancelled'),
        ('FULFILLED', 'Fulfilled')
    ])

    class Meta:
        permissions = [
            ("can_approve_order","Can Approve Order")
        ]
    def __str__(self):
        return self.order_reference
