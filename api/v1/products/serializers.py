from rest_framework import serializers
from products.models import *
from django.db.models import Sum

class AddCategorySerializers(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    image = serializers.FileField()


class ViewCategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = (
            'id',
            'name',
            'description',
            'image'
        )


class ProductAdminViewSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    stock = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'description',
            'category',
            'purchase_price',
            'price',
            'stock',
            'status'
        )
    def get_category(self,instance):
        category = instance.subcategory.category.name
        sub = instance.subcategory.name
        name = category + '-' + sub
        return name
    def get_stock(self, instance):
        stock = ProductItem.objects.aggregate(total_stock=Sum('stock'))
        return stock["total_stock"]

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('id',
                  'name',
                  'description'
                  )
class AddProductSerializer(serializers.Serializer):
    subcategory_id = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)  
    offers = serializers.IntegerField()  
    company_id = serializers.CharField()
    purchase_price = serializers.DecimalField(max_digits=10, decimal_places=2)


class AddCategorySerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    image = serializers.FileField()


class AddSubCategorySerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()


class AddProductItemSerializer(serializers.Serializer):
    color = serializers.CharField()
    stock = serializers.IntegerField()
    size = serializers.IntegerField()
    # quantity = serializers.IntegerField()
    images = serializers.ListField(child=serializers.FileField())