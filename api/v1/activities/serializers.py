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
    
    
    
    


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'quantity', 'price']

class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'total_amount', 'cart_items']
