from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User
from django.db import models
from main.models import *
from django.db import models
from main.models import *
from django.contrib.auth.models import Group
from products.models import Product 
from accounts.models import Address

PAYMENT_METHOD = [
    ('cod', 'Cash on delivery'),
    ('card','CARD'),
    ('ot','Online transaction')
]

LOG_STATUS = [
    ("pending", "Pending"),
    ("ordered", "Ordered"),
    ("confirmed", "Confirmed"),
    ("packed", "Packed"),
    ("shipped", "Shipped"),
    ("delivered", "Delivered"),
    ("cancelled", "Cancelled"),
    ("return_dispatched", "Return Dispatched"),
    ("return_received", "Return Received"),
    ("payment_failed", "Payment Failed"),
    ("shipment_failed", "Shipment Failed"),
]
class ActivityLog(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=100)
    product = models.ForeignKey('products.Product', related_name='products', on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}"
    

class PurchaseAmount(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10,decimal_places=2, blank=True, null=True)
    tax =  models.DecimalField(max_digits=10,decimal_places=2, blank=True, null=True)
    final_amount = models.DecimalField(max_digits=10,decimal_places=2, blank=True, null=True)
    wallet_deduction = models.DecimalField(max_digits=10,decimal_places=2, blank=True, null=True)
    payment_method = models.CharField(choices=PAYMENT_METHOD, max_length=155, default='cod')

    # class Meta:
    #     db_table = 'activities_purchases'
    #     managed = True
    #     verbose_name = 'Purchase Amount'
    #     verbose_name_plural = 'Purchase Amount'

    # def __str__(self):
    #     return self.user
    

class Refferals(BaseModel):
    refered_by = models.ForeignKey('accounts.UserProfile',on_delete=models.CASCADE,blank=True,null=True,related_name="refered_by")
    refered_to = models.ForeignKey('accounts.UserProfile',on_delete=models.CASCADE,blank=True,null=True,related_name="refered_to")
    completed = models.BooleanField(default=False)

    class Meta:
        db_table = 'activities_referalls'
        managed = True
        verbose_name = 'Refferals'
        verbose_name_plural = 'Refferals'

    # def __str__(self):
    #     return self.user.name
    

class PurchaseLog(BaseModel):
    Purchases = models.ForeignKey('PurchaseAmount',on_delete=models.CASCADE, blank=True, null=True)
    log_status = models.CharField(max_length=155,choices=LOG_STATUS, blank=True, null=True, default='pending')
    description = models.TextField()

    class Meta:
        db_table = 'activities_purchaselog'
        managed = True
        verbose_name = 'PurchaseLog'
        verbose_name_plural = 'Purchase logs'

    
    

# ---------wishlist model---------------



class WishlistItem(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}'s wishlist item - {self.product.name}"
    
    


# ----------cart model-------------------


 # Update this import as per your actual setup

class Cart(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.PositiveBigIntegerField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    def update_total_amount(self):
        total = sum(item.price * item.quantity for item in self.cart_items.all())
        self.total_amount = total
        self.save()

class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.PositiveBigIntegerField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.product.name} in {self.cart.user.username}'s cart"



class Purchase(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey("accounts.Address", on_delete=models.CASCADE, related_name='purchases', blank=True, null=True)
    total_amount = models.PositiveBigIntegerField(max_length=100, blank=True, null=True)
    def __str__(self):
        return f"Purchase for {self.user.username}"

    def update_total_amount(self):
        total = sum(item.price * item.quantity for item in self.PurchaseItems.all())
        self.total_amount = total
        self.save()

class PurchaseItems(BaseModel):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='purchase_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.PositiveBigIntegerField(max_length=100, blank=True, null=True)


    def __str__(self):
        return f"{self.product.name} in {self.purchase.user.username}'s purchase"



# purchase item - like cart
# purchase items - like cart itmes
    #==done
# purchase cod or online payment
# stripe payment if possible
# coin
# refferal amount manualyy enter when Purchase