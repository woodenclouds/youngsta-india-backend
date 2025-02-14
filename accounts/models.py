from django.db import models
from main.models import *
from django.contrib.auth.models import Group


class AdminProfile(BaseModel):
    name = models.CharField(max_length=155, blank=True, null=True)
    email = models.EmailField(max_length=155, blank=True, null=True)
    country_code = models.CharField(max_length=5)  # Adjust max_length as per your requirements
    phone_number = models.CharField(max_length=15) 
    password = models.TextField(blank=True, null=True)
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE)
    device_token = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        is_new = not self.pk  # Check if the instance is new

        super(AdminProfile, self).save(*args, **kwargs)

        if is_new:  # If the instance is new
            admin_group, _ = Group.objects.get_or_create(name='admin')  # Fetch or create the 'admin' group
            self.user.groups.add(admin_group)  # Add the user to the 'admin' group
            self.user.save()

    class Meta:
        db_table = "accounts_admin_profile"
        verbose_name = "Admin Profile"
        verbose_name_plural = "Admin Profiles"
        ordering = ('created_at',)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return self.phone
        

class UserProfile(BaseModel):
    name = models.CharField(max_length=155, blank=True, null=True)
    email = models.EmailField(max_length=155, blank=True, null=True)
    country_code = models.CharField(max_length=5)  # Adjust max_length as per your requirements
    phone_number = models.CharField(max_length=15) 
    password = models.TextField(blank=True, null=True)
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE)
    device_token = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        is_new = not self.pk  # Check if the instance is new

        super(AdminProfile, self).save(*args, **kwargs)

        if is_new:  # If the instance is new
            admin_group, _ = Group.objects.get_or_create(name='users')  # Fetch or create the 'admin' group
            self.user.groups.add(admin_group)  # Add the user to the 'admin' group
            self.user.save()

    class Meta:
        db_table = "accounts_admin_profile"
        verbose_name = "Admin Profile"
        verbose_name_plural = "Admin Profiles"
        ordering = ('created_at',)

    class Meta:
        db_table = "accounts_user_profile"
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ('created_at',)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return self.phone
        
class Cart(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    total_amount = models.PositiveBigIntegerField(max_length=100,blank=True,null=True)

    def __str__(self):
        return f"Cart for {self.user.name}"
    
    def update_total_price(self):
        total = sum(item.price * item.quantity for item in self.cartitem_set.all())
        self.total_price = total
        self.save()
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.PositiveBigIntegerField(max_length=100,blank=True,null=True)

    def __str__(self):
        return f"{self.product.name} in {self.cart.user.username}'s cart"