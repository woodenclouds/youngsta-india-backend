from rest_framework import serializers
from products.models import *
from django.db.models import Sum

class AddCategorySerializers(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    image = serializers.CharField()


class ViewCategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = (
            'id',
            'name',
            'description',
            'image'
        )

class ViewSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = (
            'id',
            'name',
            'description',
            'category'
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

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('id',
                  'name',
                  'description'
                  )
        

class AddBrandSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    image = serializers.CharField() 
    
    
class EditBrandSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    image = serializers.CharField()
    class Meta:
        model = Category
        fields = ['name', 'description', 'image']

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance
    
           
class AddProductSerializer(serializers.Serializer):
    subcategory_id = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)  
    offers = serializers.IntegerField()  
    brand_id = serializers.CharField()
    purchase_price = serializers.DecimalField(max_digits=10, decimal_places=2)


class AddCategorySerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    image = serializers.CharField()


class AddSubCategorySerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    parent = serializers.PrimaryKeyRelatedField(queryset=SubCategory.objects.all(), required=False, allow_null=True)



class AddProductItemSerializer(serializers.Serializer):
    color = serializers.CharField()
    stock = serializers.IntegerField()
    size = serializers.IntegerField()
    # quantity = serializers.IntegerField()
    images = serializers.ListField(child=serializers.FileField())



class EditCategorySerializer(serializers.Serializer): 
    name = serializers.CharField()
    description = serializers.CharField()
    image = serializers.CharField()
    class Meta:
        model = Category
        fields = ['name', 'description', 'image']

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance
    
class EditSubCategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    description = serializers.CharField()

    class Meta:
        model = SubCategory
        fields = ['name', 'description', 'category', 'parent']

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)

        # 'category' and 'parent' should be instances of Category and SubCategory respectively
        category_data = validated_data.get('category', None)
        parent_data = validated_data.get('parent', None)

        if category_data:
            category_instance = Category.objects.get(name=category_data)
            instance.category = category_instance

        if parent_data:
            parent_instance = SubCategory.objects.get(name=parent_data)
            instance.parent = parent_instance

        instance.save()
        return instance
    
# -------Atribute serializers-------------

class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ('id', 
                  'title', 
                  'display_name', 
                  'values')



# class AddAttributeSerializer(serializers.Serializer):
#     title = serializers.CharField(max_length=100)
#     display_name = serializers.CharField(max_length=100)
#     values = serializers.ListField(child=serializers.CharField(), allow_empty=False)




class AddAttributeSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100)
    display_name = serializers.CharField(max_length=100)
    values = serializers.CharField()  # Accepts comma-separated values

    def create(self, validated_data):
        """
        Create and return a new Attribute instance, given the validated data.
        """
        values = validated_data.pop('values', '')  # Extract 'values' from validated_data

        # Split the 'values' string by commas and convert values to integers or strings
        values_list = [int(val) if val.isdigit() else val.strip() for val in values.split(',')]

        # Add the 'values' list back to validated_data before creating the instance
        validated_data['values'] = values_list

        return Attribute.objects.create(**validated_data)








class EditAttributeSerializer(serializers.ModelSerializer):
    values = serializers.CharField()

    class Meta:
        model = Attribute
        fields = ('title', 'display_name', 'values')

    def validate_values(self, value):
        # Split the comma-separated values and return as a list
        return [val.strip() for val in value.split(',')]
    
    
    


