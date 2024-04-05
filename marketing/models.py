from django.db import models
from main.models import *
from django.db.models import Max, Value
import random 
from django.utils.text import slugify
from django.core.validators import MaxValueValidator, MinValueValidator
import random
import string


class Ads(BaseModel):
    title = models.CharField(max_length=100)
    position = models.CharField(max_length=50)
    heading = models.CharField(max_length=150, blank=True, null=True)  # Optional
    subheading = models.CharField(max_length=150, blank=True, null=True)  # Optional
    # Other fields as needed

    class Meta:
        db_table = 'advertisement_table'  # Custom table name 
        managed = True
        verbose_name_plural = 'Products'
        verbose_name = 'Ad'  # Singular display name for the model
        verbose_name_plural = 'Ads'  # Plural display name for the model



class AdsItem(BaseModel):
    advertisement = models.ForeignKey(Ads, related_name='ad_items', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    position = models.CharField(max_length=50)
    url = models.URLField()
    image = models.CharField(max_length=50)
    # Other fields as needed

    class Meta:
        db_table = 'aditem_table'  # Custom table name
        managed = True
        verbose_name = 'AdsItem'  # Singular display name for the model
        verbose_name_plural = 'AdsItems'  # Plural display name for the model

class Coupens(BaseModel):
    code = models.CharField(max_length=155, blank=True, null=True)
    offer = models.IntegerField(
        validators=[
            MaxValueValidator(99),
            MinValueValidator(10),
        ],
        blank=True,
        null=True
    )
    description = models.TextField(blank=True, null=True)
    validity = models.DateField(blank=False, null=False)   
    active = models.BooleanField(default=True)
    offer_start_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    offer_end_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table='coupens'
        managed = True
        verbose_name = 'Coupen'
        verbose_name_plural = 'Coupens'


    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_unique_code()
        super().save(*args, **kwargs)

    def generate_unique_code(self):
        characters = string.ascii_uppercase + string.digits
        generated_code = ''.join(random.choice(characters) for _ in range(15))
        while Coupens.objects.filter(code=generated_code).exists():
            generated_code = ''.join(random.choice(characters) for _ in range(15))
        return generated_code
    