from rest_framework import serializers
from activities.models import *
from django.db.models import Sum
from products.models import *

class WishlistItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    class Meta:
        model = WishlistItem
        fields = (
            'id',
            'product'
        )
    def get_product(self,instance):
        product = instance.product.name
        return product