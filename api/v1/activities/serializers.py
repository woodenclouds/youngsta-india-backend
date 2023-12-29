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



class PurchaseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseItems
        fields = ['id', 'purchase', 'product', 'quantity', 'price']

class PurchaseSerializer(serializers.ModelSerializer):
    purchase_items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Purchase
        fields = ['id', 'user', 'total_amount', 'purchase_items']



class PurchaseAmountSerializer(serializers.ModelSerializer):
    tax_amount = serializers.IntegerField()
    payment_method = serializers.CharField()

    class Meta:
        model = PurchaseAmount
        fields = ['id', 'total_amount', 'tax_amount', 'final_amount', 'payment_method']