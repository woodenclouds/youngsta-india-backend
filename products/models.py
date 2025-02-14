from django.db import models
from main.models import *
from colorfield.fields import ColorField

# Create your models here.
class Category(BaseModel):
    name = models.CharField(max_length=30)
    description = models.TextField()
    image = models.ImageField(upload_to='product/category/', blank=True, null=True)

    class Meta:
        db_table = 'product_category'
        managed = True
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name
    

class Company(BaseModel):
    name = models.CharField(max_length=255,blank=True,null=True)
    description = models.TextField()
    image = models.ImageField(upload_to='product/product/', blank=True, null=True)

    class Meta:
        db_table = 'product_company'
        managed = True
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'

    def __str__(self):
        return self.name


class ProductTag(models.Model):
    tag = models.CharField(max_length=155)

class Meta:
    db_table = 'product_tag'
    managed = True
    verbose_name = 'Tag'
    verbose_name_plural = 'Tags'


class Product(BaseModel):
    name = models.TextField()
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    offers = models.PositiveIntegerField(max_length=100,blank=True,null=True)
    company = models.ForeignKey(Company,on_delete=models.CASCADE,null=True,blank=True,related_name="company")
    category = models.ForeignKey(Category,on_delete= models.CASCADE, related_name="categories", blank=True)
    specs = models.TextField(blank=True, null=True)
    purchase_price = models.DecimalField(max_digits=8, decimal_places=2)
    class Meta:
        db_table = 'product_product'
        managed = True
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.name
    

class ProductItem(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product")
    color = ColorField(default='#FFFFFF')
    size = models.CharField(max_length=30, blank=False)
    quantity = models.PositiveIntegerField(default=1,blank=True,null=True)

    class Meta:
        db_table = 'product_productitem'
        managed = True
        verbose_name = 'ProductItem'
        verbose_name_plural = 'ProductItems'

    def __str__(self):
        return f"{self.product.name} + {self.color}"
    

class ProductImages(BaseModel):
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    product_item = models.OneToOneField(ProductItem, on_delete=models.CASCADE )

    class Meta:
        db_table = "product_images"
        verbose_name = 'ProductImage'
        verbose_name_plural = 'ProductImages'




