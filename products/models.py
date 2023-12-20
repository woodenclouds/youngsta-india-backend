from django.db import models
from main.models import *
from django.db.models import Max, Value
import random 
from django.utils.text import slugify

# from colorfield.fields import ColorField

# Create your models here.
PRODUCT_STATUS = (
    ('stocking','stocking'),
    ('damged','damaged'),
    ('selling','selling'),
)


class Category(SlugModel):
    name = models.CharField(max_length=30)
    description = models.TextField()
    image = models.TextField()
    cat_id = models.CharField(max_length=6, blank=True, null=True)
    published = models.BooleanField(default=False)

    class Meta:
        db_table = 'product_category'
        managed = True
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def get_unique_slug(self, base_slug):
        slug = base_slug

        # Check if the slug already exists
        while Category.objects.filter(slug=slug).exists():
            # Append a random number to the slug
            slug = f"{base_slug}-{random.randint(1, 999)}"

        return slug

    def save(self, *args, **kwargs):
        # Generate the base slug from the name with spaces replaced by hyphens
        base_slug = slugify(self.name)

        # Add a random number if the slug already exists
        self.slug = self.get_unique_slug(base_slug)

        super().save(*args, **kwargs)


class SubCategory(SlugModel):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name="category",null=True)
    name = models.CharField(max_length=150,blank=True,null=True)
    description = models.TextField()
    published = models.BooleanField(default=False)
    order = models.IntegerField(default=0, blank=True,null=True)
    parent = models.ForeignKey('self',on_delete=models.CASCADE, blank=True,null=True)
    class Meta:
        db_table = "product_subcategory"
        managed = True
        verbose_name = 'Sub Category'
        verbose_name_plural = 'Sub Categories'

    def __str__(self):
        return f"{self.name}-{self.category.name}"
    
    def save(self, *args, **kwargs):
        if self.parent:
            self.order = self.parent.order + 1 
        else:
            self.order = 0
        
        super().save(*args, **kwargs)


class Brand(SlugModel):
    name = models.CharField(max_length=255,blank=True,null=True)
    description = models.TextField()
    image = models.TextField()

    class Meta:
        db_table = 'product_brand'
        managed = True
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'

    def _str_(self):
        return self.name

    def get_unique_slug(self, base_slug):
        slug = base_slug

        # Check if the slug already exists
        while Brand.objects.filter(slug=slug).exists():
            # Append a random number to the slug
            slug = f"{base_slug}-{random.randint(1, 999)}"

        return slug

    def save(self, *args, **kwargs):
        # Generate the base slug from the name with spaces replaced by hyphens
        base_slug = slugify(self.name)

        # Add a random number if the slug already exists
        self.slug = self.get_unique_slug(base_slug)

        super().save(*args, **kwargs)
    
    

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
    brand = models.ForeignKey(Brand,on_delete=models.CASCADE,null=True,blank=True,related_name="brand")
    subcategory = models.ForeignKey(SubCategory,on_delete= models.CASCADE, related_name="sub_categories", blank=True)
    specs = models.TextField(blank=True, null=True)
    status = models.CharField(choices=PRODUCT_STATUS,default='stocking',blank=True,null=True)
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
    color = models.CharField(max_length = 8,blank =True,null=True)
    stock = models.PositiveIntegerField(default=0, blank=True,null=True)
    size = models.IntegerField(max_length=30, blank=False)
    quantity = models.PositiveIntegerField(default=1,blank=True,null=True)
    published = models.BooleanField(default=False)

    class Meta:
        db_table = 'product_productitem'
        managed = True
        verbose_name = 'ProductItem'
        verbose_name_plural = 'ProductItems'

    def __str__(self):
        return f"{self.product.name} + {self.color}"
    

class ProductImages(BaseModel):
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    product_item = models.ForeignKey(ProductItem, on_delete=models.CASCADE,blank=True,null=True )
    primary = models.BooleanField(default=False,blank=True,null=True)

    class Meta:
        db_table = "product_images"
        verbose_name = 'ProductImage'
        verbose_name_plural = 'ProductImages'




