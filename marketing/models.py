from django.db import models
from main.models import *
from django.db.models import Max, Value
import random 
from django.utils.text import slugify


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
