from rest_framework import serializers
from products.models import *
from django.db.models import Sum
from activities.models import *


class AddCategorySerializers(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    image = serializers.CharField()


class ViewCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ("id", "name", "description", "image", "slug")


class ViewAttributesSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Attribute
        fields = ("id", "name")

    def get_name(self, instance):
        return f"{instance.attribute}-{instance.attribute_value}"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("name",)


class SubCategoryParent(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ("name",)


class ViewSubCategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    parent = SubCategoryParent()

    class Meta:
        model = SubCategory
        fields = ("id", "name", "description", "category", "image", "parent")


class AttributeDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeDescription
        fields = ("id", "value")


class ProductAttributeSerializer(serializers.ModelSerializer):
    attribute = serializers.SerializerMethodField()

    class Meta:
        model = ProductAttribute
        fields = ("id", "attribute")

    def get_attribute(self, instance):
        attribute_description = AttributeDescription.objects.get(
            pk=instance.attribute_description.pk
        )
        attribute = ProductAttributeSerializer(
            attribute_description,
        ).data
        return attribute


class ProductAdminViewSerializer(serializers.ModelSerializer):
    stock = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    attribute = serializers.SerializerMethodField()
    attribute_type = serializers.SerializerMethodField()
    # category = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    category_id = serializers.SerializerMethodField()
    total_products_stock= serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "parent",
            "name",
            "category",
            "category_id",
            "description",
            "product_sku",
            "actual_price",
            "selling_price",
            "gst_price",
            "return_in",
            "referal_Amount",
            "attribute_type",
            "sub_category",
            "featured",
            "thumbnail",
            "images",
            "attribute",
            "weight",
            "height",
            "length",
            "width",
            "stock",
            "published",
            "flash_sale",
            "total_products_stock",
          
        )

    def get_stock(self, instance):
        stock = ProductAttribute.objects.filter(product=instance).aggregate(total_stock=Sum("quantity"))
        return stock["total_stock"]

    def get_total_products_stock(self, instance):
        products = Product.objects.filter(parent=instance, is_parent=False)  # Get child variants
        all_products = list(products) + [instance]
        product_variant_count = len(all_products)

        total_stock = ProductAttribute.objects.filter(product__in=all_products).aggregate(total_stock=Sum("quantity"))

        return {
            "total_stock": total_stock["total_stock"] or 0,  
            "product_varient_count": product_variant_count,
        }

    def get_thumbnail(self, instance):
        image = None

        if ProductImages.objects.filter(product=instance, thumbnail=True).exists():
            image = ProductImages.objects.filter(product=instance, thumbnail=True).latest('created_at')
            if image:
                image = image.image
        return image

    def get_attribute(self, instance):
        attributes = ProductAttribute.objects.filter(product=instance)
        serialized = ProductAttributeDescriptionSerializer(
            attributes,
            many=True,
        ).data
        return serialized
    
    def get_attribute_type(self, instance):
        attributes = ProductAttribute.objects.filter(product=instance)
        if not attributes.exists():
            return None
        # Assuming each product has attributes with the same attribute type
        attribute_type = attributes.first().attribute_description.attribute_type
        values = []
        attribute_descriptions = AttributeDescription.objects.filter(attribute_type=attribute_type)
        for attribute_description in attribute_descriptions:
            values.append({
                "id": attribute_description.id,
                "value": attribute_description.value,
            })
        data = {
            "id": attribute_type.id,
            "name": attribute_type.name,
            "values": values
        }
        return data


    def get_category(self, instance):
        if instance.sub_category and instance.sub_category.category:
            category = instance.sub_category.category.name
        else:
            category = ""
        return category
    
    def get_category_id(self, instance):
        if instance.sub_category and instance.sub_category.category:
            return instance.sub_category.category.id
        return None

    def get_images(self, instance):
        product_images = ProductImages.objects.filter(product=instance)
        serialized = ProductImageSerializer(product_images, many=True).data
        return serialized

    # def get_subcategory(sel, instance):
    #     subcategory = instance.sub_category
    #     subcategory = {
    #         "id":SubCategory.id,
    #         "name":SubCategory.name,
    #     }
    #     return subcategory


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ("id", "name", "description")


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
        fields = ["name", "description", "image"]

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.description = validated_data.get("description", instance.description)
        instance.image = validated_data.get("image", instance.image)
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


class AddAttributesSerializer(serializers.Serializer):
    attribute = serializers.CharField()
    attribute_value = serializers.CharField()


class AddCategorySerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    image = serializers.CharField()


class PartialUpdateCategory:
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class EditCategorySerializer(PartialUpdateCategory, serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    image = serializers.CharField()


class AddSubCategorySerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    parent = serializers.PrimaryKeyRelatedField(
        queryset=SubCategory.objects.all(), required=False, allow_null=True
    )


class AddProductItemSerializer(serializers.Serializer):
    color = serializers.CharField()
    stock = serializers.IntegerField()
    size = serializers.IntegerField()
    # quantity = serializers.IntegerField()
    images = serializers.ListField(child=serializers.FileField())


class PartialUpdateMixin:
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class EditSubCategorySerializer(PartialUpdateMixin, serializers.ModelSerializer):
    name = serializers.CharField()
    description = serializers.CharField()
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), allow_null=True, required=False
    )
    parent = serializers.PrimaryKeyRelatedField(
        queryset=SubCategory.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = SubCategory
        fields = ["name", "description", "category", "parent"]


class EditCategoryPositionSerializer(serializers.ModelSerializer):
    position = serializers.IntegerField()

    class Meta:
        model = Category
        fields = ["position"]


class EditSubCategoryPositionSerializer(serializers.ModelSerializer):
    position = serializers.IntegerField()

    class Meta:
        model = SubCategory
        fields = ["position"]


# -------Atribute serializers-------------


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ("id", "title", "display_name", "values")


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
        values = validated_data.pop(
            "values", ""
        )  # Extract 'values' from validated_data

        # Split the 'values' string by commas and convert values to integers or strings
        values_list = [
            int(val) if val.isdigit() else val.strip() for val in values.split(",")
        ]

        # Add the 'values' list back to validated_data before creating the instance
        validated_data["values"] = values_list

        return Attribute.objects.create(**validated_data)


class EditAttributeSerializer(serializers.ModelSerializer):
    values = serializers.CharField()

    class Meta:
        model = Attribute
        fields = ("title", "display_name", "values")

    def validate_values(self, value):
        # Split the comma-separated values and return as a list
        return [val.strip() for val in value.split(",")]

    # ------------Products ----------------------------------------------------------------


class ProductAttributeDescriptionSerializer(serializers.ModelSerializer):
    attributeDescription_name = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()
    attributeDescription = serializers.SerializerMethodField()
    attribute_type = serializers.SerializerMethodField()

    class Meta:
        model = ProductAttribute
        fields = ("id", "attributeDescription_name", "value", "quantity","attributeDescription","attribute_type","sku","barcode","price")

    def get_value(self, instance):
        value = instance.attribute_description.value
        return value
    
    def get_attributeDescription(self, instance):
        value = instance.attribute_description.id if instance.attribute_description else None
        return value
    def get_attributeDescription_name(self, instance):
        value = instance.attribute_description.attribute_type.name
        return value
    
    def get_attribute_type(self,instance):
        return instance.attribute_description.attribute_type.id if instance.attribute_description else None


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = ("id", "image", "thumbnail")

class ProductGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductGallery
        fields = ("id", "image_url", "image_name")



class ProductViewSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    attribute = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    is_wishlist = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "category",
            "description",
            "selling_price",
            "thumbnail",
            "images",
            "attribute",
            "referal_Amount",
            "is_wishlist",
        )

    def get_thumbnail(self, instance):
        try:
            image = ProductImages.objects.filter(product=instance, thumbnail=True).latest("created_at")
            return image.image
        except ProductImages.DoesNotExist:
            return None  # Handle the case where no thumbnail is found

    def get_category(self, instance):
        if instance.sub_category and instance.sub_category.category:
            category = instance.sub_category.category.name
        else:
            category = ""
        return category

    def get_attribute(self, instance):
        attributes = ProductAttribute.objects.filter(product=instance, quantity__gt=0)
        
        serialized = ProductAttributeDescriptionSerializer(
            attributes,
            many=True,
        ).data
        return serialized

    def get_images(self, instance):
        product_images = ProductImages.objects.filter(product=instance)
        serialized = ProductImageSerializer(product_images, many=True).data
        return serialized

    def get_is_wishlist(self, instance):
        request = self.context.get("request")
        user_id = request.user.id
        print(user_id)

        if user_id :
            user = User.objects.get(pk=user_id)
            if WishlistItem.objects.filter(user=user, product=instance).exists():
                return True
            else:
                return False
        else:
            return False

class ProductsViewSerializer(serializers.ModelSerializer):
    # thumbnail = serializers.SerializerMethodField()
    attribute = serializers.SerializerMethodField()
    # images = serializers.SerializerMethodField()
    # is_wishlist = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "attribute",

            # "description",
            # "selling_price",
            # "thumbnail",
            # "images",
            # "referal_Amount",
            # "is_wishlist",
        )

    def get_attribute(self, instance):
        attributes = ProductAttribute.objects.filter(product=instance, quantity__gt=0)
        
        serialized = ProductAttributeDescriptionSerializer(
            attributes,
            many=True,
        ).data
        return serialized

class SubCategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = SubCategory
        fields = ["id", "name", "description", "children"]

    def get_children(self, obj):
        children = SubCategory.objects.filter(parent=obj)
        serializer = SubCategorySerializer(children, many=True)
        return serializer.data


class ProductFilterSerializer(serializers.Serializer):
    min_price = serializers.DecimalField(
        max_digits=8, decimal_places=2, required=False, allow_null=True
    )
    max_price = serializers.DecimalField(
        max_digits=8, decimal_places=2, required=False, allow_null=True
    )


# class ProductSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Product
#         fields = '__all__'

# class ProductListByPurchasePriceSerializer(serializers.Serializer):
#     message = ProductSerializer(many=True)


class VarientImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = ("id", "image", "primary")


class ProductVarientsSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()

    class Meta:
        model = ProductVarient
        fields = ("id", "images", "quantity")

    def get_images(self, instance):
        request = self.context["request"]
        instances = ProductImages.objects.filter(product_varient=instance)
        serialized = VarientImagesSerializer(
            instances, context={"request": request}, many=True
        ).data
        return serialized

    def get_quantity(self, instance):
        quantity = VarientAttribute.objects.filter(varient=instance).aggregate(
            Sum("quantity")
        )["quantity__sum"]
        return quantity


class ProductAdminSerializer(serializers.ModelSerializer):
    stock = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    attribute = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "category",
            "description",
            "product_sku",
            "actual_price",
            "selling_price",
            "referal_Amount",
            "featured",
            "thumbnail",
            "attribute",
            "stock",
            "images",
            "published",
            "flash_sale",
        )

    def get_stock(self, instance):
        stock = ProductAttribute.objects.aggregate(total_stock=Sum("quantity"))
        return stock["total_stock"]

    def get_thumbnail(self, instance):
        image = ProductImages.objects.get(product=instance, thumbnail=True)
        return image.image

    def get_attribute(self, instance):
        attributes = ProductAttribute.objects.filter(product=instance)
        serialized = ProductAttributeDescriptionSerializer(
            attributes,
            many=True,
        ).data
        return serialized

    def get_category(self, instance):
        category = instance.sub_category.category.name
        return category

    def get_images(self, instance):
        images = ProductImages.objects.filter(product=instance)
        img_serializer = ImagesSerializer(images, many=True).data
        return img_serializer


class ImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = ("id", "image", "thumbnail")


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"

    # Add 'required=False' to make certain fields not required
    weight = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    length = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    height = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    width = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    referal_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=True
    )

class AttributeTypeSerializer(serializers.ModelSerializer):
    values = serializers.SerializerMethodField()

    class Meta:
        model = AttributeType
        fields = ("id", "name", "values")

    def get_values(self, instance):
        attribute_description = AttributeDescription.objects.filter(
            attribute_type=instance
        )
        serialized = AttributeDescriptionSerializer(
            attribute_description, many=True
        ).data
        return serialized


class AttributeDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeDescription
        fields = ("id", "value")


class ProductWithCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("id", "name")


class InventorySerializers(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    attribute_detail = serializers.SerializerMethodField()
    stock = serializers.SerializerMethodField()

    class Meta:
        model = ProductAttribute
        fields = ("id","name","attribute_detail","thumbnail","stock")

    def get_name(slef, instance):
        if instance.product:
            return instance.product.name
        
    def get_stock(slef, instance):
        if instance:
            return instance.quantity
        
        
    def get_attribute_detail(self, instance):
        if instance.attribute_description:
            return {
                "attribute_type":instance.attribute_description.attribute_type.name,
                "value":instance.attribute_description.value
            }

    def get_thumbnail(self, instance):
        if instance.product:
            if ProductImages.objects.filter(product=instance.product, thumbnail=True).exists():
                image = ProductImages.objects.filter(product=instance.product, thumbnail=True).latest("created_at")
                return image.image        
        else:
            return None


class ProductStockSerialier(serializers.ModelSerializer):
    attribute_description = serializers.SerializerMethodField()

    class Meta:
        model = ProductAttribute
        fields = ("id", "quantity", "attribute_description")

    def get_attribute_description(self, instance):
        attribute = instance.attribute_description.value
        return attribute


class AttributeViewSerializer(serializers.ModelSerializer):
    attribute_description = serializers.SerializerMethodField()

    class Meta:
        model = AttributeType
        fields = ("id", "name", "attribute_description")

    def get_attribute_description(self, obj):
        instances = AttributeDescription.objects.filter(attribute_type=obj)
        serialized = AttributeDescriptionViewSerializer(instances, many=True).data
        return serialized


class AttributeDescriptionViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeDescription
        fields = (
            "id",
            "value",
        )

class ProductAttributeNameSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    attribute_description = serializers.SerializerMethodField()

    class Meta:
        model = ProductAttribute
        fields = (
            'id',
            'product_name',
            'attribute_description',
        )

    def get_product_name(self, instance):
        if instance.product.name:
            product_name = instance.product.name
            return product_name
    
    def get_attribute_description(self, instance):
        if instance.attribute_description:
            return {
                "attribute_type":instance.attribute_description.attribute_type.name,
                "value":instance.attribute_description.value
            }