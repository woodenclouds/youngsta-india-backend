from django.db import models
from main.models import *
from django.db.models import Max, Value
import random
from django.utils.text import slugify
from datetime import timedelta
from django.utils import timezone
import string

# from colorfield.fields import ColorField

# Create your models here.
PRODUCT_STATUS = (
    ("stocking", "stocking"),
    ("damged", "damaged"),
    ("selling", "selling"),
)


class Category(SlugModel):
    name = models.CharField(max_length=30)
    description = models.TextField()
    image = models.TextField()
    cat_id = models.CharField(max_length=6, blank=True, null=True)
    published = models.BooleanField(default=False)
    position = models.IntegerField(default=0)

    class Meta:
        db_table = "product_category"
        managed = True
        verbose_name = "Category"
        verbose_name_plural = "Categories"

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
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, related_name="category", null=True
    )
    name = models.CharField(max_length=150, blank=True, null=True)
    description = models.TextField()
    published = models.BooleanField(default=False)
    order = models.IntegerField(default=0, blank=True, null=True)
    position = models.IntegerField(default=0)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = "product_subcategory"
        managed = True
        verbose_name = "Sub Category"
        verbose_name_plural = "Sub Categories"

    def __str__(self):
        if self.category:
            return f"{self.name}-{self.category.name}"
        else:
            return f"{self.name}"

    def save(self, *args, **kwargs):
        if self.parent:
            self.order = self.parent.order + 1
        else:
            self.order = 0

        base_slug = slugify(self.name)

        # Add a random number if the slug already exists
        self.slug = self.get_unique_slug(base_slug)

        super().save(*args, **kwargs)

    # slug
    def get_unique_slug(self, base_slug):
        slug = base_slug

        # Check if the slug already exists
        while SubCategory.objects.filter(slug=slug).exists():
            # Append a random number to the slug
            slug = f"{base_slug}-{random.randint(1, 999)}"

        return slug


class Brand(SlugModel):
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    image = models.TextField()

    class Meta:
        db_table = "product_brand"
        managed = True
        verbose_name = "Brand"
        verbose_name_plural = "Brands"

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
    db_table = "product_tag"
    managed = True
    verbose_name = "Tag"
    verbose_name_plural = "Tags"


# class Product(BaseModel):
#     name = models.TextField()
#     description = models.TextField()
#     price = models.DecimalField(max_digits=8, decimal_places=2)
#     offers = models.PositiveIntegerField(max_length=100,blank=True,null=True)
#     brand = models.ForeignKey(Brand,on_delete=models.CASCADE,null=True,blank=True, related_name="brand")
#     subcategory = models.ForeignKey(SubCategory,on_delete= models.CASCADE, related_name="sub_categories", blank=True)
#     specs = models.TextField(blank=True, null=True)
#     status = models.CharField(choices=PRODUCT_STATUS,default='stocking',blank=True,null=True)
#     purchase_price = models.DecimalField(max_digits=8, decimal_places=2)

#     class Meta:
#         db_table = 'product_product'
#         managed = True
#         verbose_name = 'Product'
#         verbose_name_plural = 'Products'

#     def __str__(self):
#         return  self.name


class Product(models.Model):
    name = models.TextField()
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_code = models.CharField(max_length=15, blank=True, null=True)
    is_parent = models.BooleanField(default=True, blank=True, null=True)
    sub_category = models.ForeignKey(
        "SubCategory", on_delete=models.CASCADE, blank=True, null=True
    )
    product_sku = models.CharField(max_length=50, blank=True, null=True)
    return_in = models.IntegerField()  # Fix the typo here
    actual_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    selling_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    referal_Amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    featured = models.BooleanField(default=False, blank=True, null=True)
    flash_sale = models.BooleanField(default=False, blank=True, null=True)
    offer = models.IntegerField(blank=True, null=True)
    published = models.BooleanField(default=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = "products"
        managed = True
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.product_code:
            self.product_code = self.generate_unique_code()
        super().save(*args, **kwargs)

    def generate_unique_code(self):
        characters = string.ascii_uppercase + string.digits
        generated_code = "".join(random.choice(characters) for _ in range(8))
        while Product.objects.filter(product_code=generated_code).exists():
            generated_code = "".join(random.choice(characters) for _ in range(8))
        return generated_code


class ProductImages(BaseModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, blank=True, null=True
    )
    image = models.TextField()
    thumbnail = models.BooleanField(default=False, blank=True, null=True)

    class Meta:
        db_table = "product_image"
        managed = True
        verbose_name = "Product image"
        verbose_name_plural = "Product images"


class AttributeType(BaseModel):
    name = models.CharField(max_length=155, blank=True, null=True)

    class Meta:
        db_table = "attribute_type"
        managed = True
        verbose_name = "Attribute Type"
        verbose_name_plural = "Attribute Types"

    def __str__(self):
        return self.name


class AttributeDescription(BaseModel):
    attribute_type = models.ForeignKey(
        AttributeType, on_delete=models.CASCADE, blank=True, null=True
    )
    value = models.CharField(max_length=155, blank=True, null=True)

    class Meta:
        db_table = "attribute_description"
        managed = True
        verbose_name = "Attribute Description"
        verbose_name_plural = "Attribute Descriptions"

    def __str__(self):
        return f"{self.attribute_type.name}-{self.value}"


class ProductAttribute(BaseModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, blank=True, null=True
    )
    attribute_description = models.ForeignKey(
        AttributeDescription, on_delete=models.CASCADE, blank=True, null=True
    )
    quantity = models.IntegerField()

    class Meta:
        db_table = "product_attribute"
        managed = True
        verbose_name = "Product Attribute"
        verbose_name_plural = "Product Attribute"

    def __str__(self):
        return f"{self.attribute_description.value}-{self.quantity}"


class ProductItem(BaseModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product"
    )
    color = models.CharField(max_length=8, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0, blank=True, null=True)
    size = models.IntegerField(max_length=30, blank=False)
    quantity = models.PositiveIntegerField(default=1, blank=True, null=True)
    published = models.BooleanField(default=False)

    class Meta:
        db_table = "product_productitem"
        managed = True
        verbose_name = "ProductItem"
        verbose_name_plural = "ProductItems"

    def __str__(self):
        return f"{self.product.name} + {self.color}"


class ProductVarient(BaseModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, blank=True, null=True
    )
    thumbnail = models.TextField()
    quantity = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = "product_varient"
        verbose_name = "ProductVarient"
        verbose_name_plural = "ProductVarients"


# class ProductImages(BaseModel):
#     image = models.TextField()
#     product_varient = models.ForeignKey(ProductVarient, on_delete=models.CASCADE,blank=True,null=True )
#     primary = models.BooleanField(default=False,blank=True,null=True)

#     class Meta:
#         db_table = "product_images"
#         verbose_name = 'ProductImage'
#         verbose_name_plural = 'ProductImages'


# --------------model for attributes-------------
class Attribute(BaseModel):
    # product_varient = models.ForeignKey(ProductVarient, on_delete=models.CASCADE,blank=True,null=True )
    # quantity = models.IntegerField(blank=True, null=True)
    attribute = models.CharField(max_length=255, blank=True, null=True)
    attribute_value = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "product_attributes"
        managed = True
        verbose_name = "Attribute"
        verbose_name_plural = "Attributes"


class VarientAttribute(BaseModel):
    varient = models.ForeignKey(
        ProductVarient, on_delete=models.CASCADE, blank=True, null=True
    )
    attribute = models.ForeignKey(
        Attribute, on_delete=models.CASCADE, blank=True, null=True
    )
    quantity = models.IntegerField(max_length=155, blank=True, null=True)

    class Meta:
        db_table = "product_varient_attribute"
        managed = True
        verbose_name = "Varient Attribute"
        verbose_name_plural = "Varient Attributes"

    def __str__(self):
        return f"{self.varient.product.name} -- {self.attribute.attribute}-{self.attribute.attribute_value}"
