from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User
from django.db import models
from main.models import *
from django.db import models
from main.models import *
from django.contrib.auth.models import Group
from products.models import Product, ProductVarient, VarientAttribute
from accounts.models import Address
from django.db.models.signals import post_save
from django.dispatch import receiver
import string
import random

PAYMENT_METHOD = [
    ("cod", "Cash on delivery"),
    ("card", "CARD"),
    ("ot", "Online transaction"),
]

REFFERAL_STATUS = (
    ("pending", "Pending"),
    ("purchased", "Purchased"),
    ("purchase_completed", "Purchase Completed"),
    ("completed", "Completed"),
)

LOG_STATUS = [
    ("Pending", "Pending"),
    ("Accepted", "Accepted"),
    ("Shipped", "Shipped"),
    ("Delivered", "Delivered"),
    ("Cancelled", "Cancelled"),
    ("Return", "Return"),
]

RETURN_CHOICE = [
    ("pending", "Pending"),
    ("accepted", "Accepted"),
    ("rejected", "Rejected"),
    ("collected", "Collected"),
    ("refund", "Refund"),
    ("completed", "Completed"),
]


class ActivityLog(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=100)
    product = models.ForeignKey(
        "products.Product", related_name="products", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}"


class PurchaseAmount(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    tax = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    final_amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    wallet_deduction = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    payment_method = models.CharField(
        choices=PAYMENT_METHOD, max_length=155, default="cod"
    )

    # class Meta:
    #     db_table = 'activities_purchases'
    #     managed = True
    #     verbose_name = 'Purchase Amount'
    #     verbose_name_plural = 'Purchase Amount'

    # def __str__(self):
    #     return self.user


class Refferals(BaseModel):
    refered_by = models.ForeignKey(
        "accounts.UserProfile",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="refered_by",
    )
    refered_to = models.ForeignKey(
        "accounts.UserProfile",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="refered_to",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="reffered_product",
    )
    completed = models.BooleanField(default=False)

    class Meta:
        db_table = "activities_referalls"
        managed = True
        verbose_name = "Refferals"
        verbose_name_plural = "Refferals"

    # def __str__(self):
    #     return self.user.name


class PurchaseLog(BaseModel):
    Purchases = models.ForeignKey(
        "Purchase", on_delete=models.CASCADE, blank=True, null=True
    )
    log_status = models.CharField(
        max_length=155, choices=LOG_STATUS, blank=True, null=True, default="pending"
    )
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "activities_purchaselog"
        managed = True
        verbose_name = "PurchaseLog"
        verbose_name_plural = "Purchase logs"


# ---------wishlist model---------------


class WishlistItem(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}'s wishlist item - {self.product.name}"


# ----------cart model-------------------


# Update this import as per your actual setup


class Cart(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.PositiveBigIntegerField( blank=True, null=True)
    coupen_offer = models.PositiveBigIntegerField( blank=True, null=True)
    coupon_code = models.CharField(max_length=155, blank=True, null=True)
    product_total = models.PositiveBigIntegerField( blank=True, null=True)
    
    def __str__(self):
        return f"Cart for {self.user.username}"

    def save(self, *args, **kwargs):
        if self.product_total is not None and self.coupen_offer is not None:
            self.total_amount = self.product_total - self.coupen_offer
        super().save(*args, **kwargs)


class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(
        "products.Product", on_delete=models.CASCADE, blank=True, null=True
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.PositiveBigIntegerField(blank=True, null=True)
    attribute = models.ForeignKey(
        "products.ProductAttribute", on_delete=models.CASCADE, blank=True, null=True
    )
    referral_code = models.CharField(max_length=155, blank=True, null=True)
    coupon_code = models.CharField(max_length=155, blank=True, null=True)
    def __str__(self):
        return f"{self.product.name} in {self.cart.user.username}'s cart"

class Sources(BaseModel):
    name = models.CharField(max_length=255, blank=True, null=True)
 
    def __str__(self):
        return f"{self.name}-{self.id}"

    class Meta:
        db_table = "activities_sources"
        managed = True
        verbose_name = "Source"
        verbose_name_plural = "Sources"


class Purchase(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(
        "accounts.Address",
        on_delete=models.CASCADE,
        related_name="purchases",
        blank=True,
        null=True,
    )
    total_amount = models.PositiveBigIntegerField(blank=True, null=True)
    status = models.CharField(choices=LOG_STATUS, blank=True, null=True)
    order_status = models.CharField(max_length=255, blank=True, null=True)
    refferal = models.CharField(max_length=10, blank=True, null=True)
    active = models.BooleanField(default=True, blank=True, null=True)
    invoice_no = models.CharField(max_length=10, blank=True, null=True)
    method = models.CharField(choices=PAYMENT_METHOD, blank=True, null=True)
    source = models.ForeignKey(Sources, on_delete=models.CASCADE, blank=True, null=True)
  

    def __str__(self):
        return f"Purchase for {self.user.username}"

    def update_total_amount(self):
        total = sum(item.price * item.quantity for item in self.PurchaseItems.all())
        self.total_amount = total
        self.save()

    def save(self, *args, **kwargs):
        import random
        import string
        if not self.invoice_no:
            self.invoice_no = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        super().save(*args, **kwargs)
        
class PurchaseItems(BaseModel):
    purchase = models.ForeignKey(
        Purchase, on_delete=models.CASCADE, related_name="purchase_items"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    attribute = models.ForeignKey(
        "products.ProductAttribute", on_delete=models.CASCADE, blank=True, null=True
    )
    price = models.PositiveBigIntegerField(blank=True, null=True)
    is_returned = models.BooleanField(default=False, blank=True, null=True)
    is_cancelled = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return f"{self.product.name} in {self.purchase.user.username}'s purchase"


# purchase item - like cart
# purchase items - like cart itmes
# ==done
# purchase cod or online payment
# stripe payment if possible
# coin
# refferal amount manualyy enter when Purchase


class PurchaseStatus(BaseModel):
    status = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    order_id = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.status}-{self.order_id}"

    class Meta:
        db_table = "activities_purchase_status"
        managed = True
        verbose_name = "Purchase Status"
        verbose_name_plural = "Purchase Statuses"


class PurchaseLogs(BaseModel):
    purchase = models.ForeignKey(
        Purchase, on_delete=models.CASCADE, blank=True, null=True
    )
    status = models.ForeignKey(
        PurchaseStatus, on_delete=models.CASCADE, blank=True, null=True
    )
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "activities_purchase_log"
        managed = True
        verbose_name = "Purchase Log"
        verbose_name_plural = "Purchase Logs"


class Referral(BaseModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="referrals"
    )
    referred_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="referrals_made"
    )
    referred_to = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="referrals_received"
    )
    referral_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order = models.ForeignKey(
        Purchase, on_delete=models.CASCADE, related_name="referrals"
    )
    refferal_status = models.CharField(
        choices=REFFERAL_STATUS, max_length=155, blank=True, null=True
    )
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Referral from {self.referred_by.username} to {self.referred_to.username} for {self.product.name}"

    class Meta:
        db_table = "activities_referral"
        managed = True
        verbose_name = "Referral"
        verbose_name_plural = "Referrals"

class ReturnStatusLog(BaseModel):
    status = models.CharField(choices = RETURN_CHOICE ,max_length=155, blank=True, null=True)
    return_model = models.ForeignKey('Return', related_name='return_mod', on_delete=models.CASCADE)
    class Meta:
        db_table = "activities_return_status"
        managed = True
        verbose_name = "Return Status"
        verbose_name_plural = "Return Status"

class Return(BaseModel):
    purchase_item = models.ForeignKey('PurchaseItems', related_name='purchase_item', on_delete=models.CASCADE)
    reason = models.TextField(blank=True, null=True)
    return_remarks = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "activities_return"
        managed = True
        verbose_name = "Return"
        verbose_name_plural = "Returns"

    