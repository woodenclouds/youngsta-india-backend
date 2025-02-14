from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User
from django.db import models
from main.models import *


PAYMENT_METHOD = [
    ('cod', 'Cash on delivery'),
    ('card','CARD'),
    ('ot','Online transaction')
]

LOG_STATUS = [
    ('packed', 'Packed'),
    ('shipment_dispatched','Shipment dispatched'),
    ('transporting','Transporting'),
    ('shipment_reached', 'Shipment reached'),
    ('out_for_delivery','Out for delivery')
]
class ActivityLog(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=100)
    product = models.ForeignKey('products.Product', related_name='products', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}"
    

class Purchases(BaseModel):
    total_amount = models.DecimalField(max_digits=10,decimal_places=2, blank=True, null=True)
    tax =  models.DecimalField(max_digits=10,decimal_places=2, blank=True, null=True)
    final_amount = models.DecimalField(max_digits=10,decimal_places=2, blank=True, null=True)
    payment_method = models.CharField(choices=PAYMENT_METHOD, max_length=155, default='cod')

    class Meta:
        db_table = 'activities_purchases'
        managed = True
        verbose_name = 'Purchase'
        verbose_name_plural = 'Purchases'

    def __str__(self):
        return self.user.name
    

class Refferals(BaseModel):
    refered_by = models.ForeignKey('accounts.UserProfile',on_delete=models.CASCADE,blank=True,null=True,related_name="refered_by")
    refered_to = models.ForeignKey('accounts.UserProfile',on_delete=models.CASCADE,blank=True,null=True,related_name="refered_to")
    completed = models.BooleanField(default=False)

    class Meta:
        db_table = 'activities_referalls'
        managed = True
        verbose_name = 'Refferals'
        verbose_name_plural = 'Refferals'

    def __str__(self):
        return self.user.name
    

class PurchaseLog(BaseModel):
    Purchases = models.ForeignKey('Purchases',on_delete=models.CASCADE, blank=True, null=True)
    log_status = models.CharField(max_length=155,choices=LOG_STATUS, blank=True, null=True)
    description = models.TextField()

    class Meta:
        db_table = 'activities_purchaselog'
        managed = True
        verbose_name = 'Purchase log'
        verbose_name_plural = 'Purchase logs'

    
    

    
    
