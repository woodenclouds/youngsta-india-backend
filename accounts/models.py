from django.db import models
from main.models import *
from django.contrib.auth.models import Group
from django.contrib.auth.models import User


STAFF_TYPE = [
    ('manager', 'Manager'),
    ('staff','staff'),
]


class AdminProfile(BaseModel):
    name = models.CharField(max_length=155, blank=True, null=True)
    email = models.EmailField(max_length=155, blank=True, null=True)
    password = models.TextField(blank=True, null=True)
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE)
    country_code = models.CharField(max_length=5, blank=True, null=True)
    phone_number = models.CharField(max_length=155, blank=True, null=True)
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
    first_name = models.CharField(max_length=155, blank=True, null=True)
    last_name = models.CharField(max_length=155, blank=True, null=True)
    email = models.EmailField(max_length=155, blank=True, null=True)
    country_code = models.CharField(max_length=5)  # Adjust max_length as per your requirements
    phone_number = models.CharField(max_length=15) 
    password = models.TextField(blank=True, null=True)
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)
    refferal_code = models.CharField(max_length=10,blank=True, null=True)
    device_token = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        is_new = not self.pk  # Check if the instance is new

        super(UserProfile, self).save(*args, **kwargs)  # Call the parent's save method using UserProfile
        if is_new:  # If the instance is new
            admin_group, _ = Group.objects.get_or_create(name='users')  # Fetch or create the 'users' group
            self.user.groups.add(admin_group)  # Add the user to the 'users' group
            self.user.save()

    
    class Meta:
        db_table = "accounts_user_profile"
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ('created_at',)

    def __str__(self):
          if self.first_name and self.last_name:
              return f"{self.first_name} {self.last_name}"
          elif self.phone_number:
              return self.phone_number
          else:
              return "UserProfile"

class Address(BaseModel):
    first_name = models.CharField(max_length=155, blank=True, null=True)
    last_name = models.CharField(max_length=155, blank=True, null=True)
    phone = models.CharField(max_length = 155, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    street = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    post_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, blank=True,null=True)
    primary = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state} {self.post_code}, {self.country}"




# class Cart(models.Model):
#     user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
#     total_amount = models.PositiveBigIntegerField(max_length=100,blank=True,null=True)

#     def __str__(self):
#         return f"Cart for {self.user.name}"
    
#     def update_total_price(self):
#         total = sum(item.price * item.quantity for item in self.cartitem_set.all())
#         self.total_price = total
#         self.save()
    
# class CartItem(models.Model):
#     cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
#     product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)
#     price = models.PositiveBigIntegerField(max_length=100,blank=True,null=True)

#     def __str__(self):
#         return f"{self.product.name} in {self.cart.user.username}'s cart"




class Staff(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    password = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=100, choices=STAFF_TYPE, blank=True, null=True, default='staff')


    def __str__(self):
        return f"{self.fullname} - {self.type}"