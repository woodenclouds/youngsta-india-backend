from rest_framework import serializers
from activities.models import *
from django.db.models import Sum
from products.models import *
from api.v1.products.serializers import *
from datetime import datetime
from payments.models import *
from django.core.exceptions import ObjectDoesNotExist
from accounts.models import *

import ast
import random
import string


class WishlistItemSerializer(serializers.ModelSerializer):
    product_info = serializers.SerializerMethodField()

    class Meta:
        model = WishlistItem
        fields = (
            "id",
            "product_info",
        )

    def get_product_info(self, instance):
        request = self.context.get("request")
        product = Product.objects.get(pk=instance.product.id)
        serialized = ProductViewSerializer(product,context={"request":request}).data
        return serialized


class CartItemSerializer(serializers.ModelSerializer):
    product_info = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = (
            "id",
            "cart",
            "quantity",
            "price",
            "product_info",
        )

    def get_product_info(self, instance):
        request = self.context.get("request")
        product = Product.objects.get(pk=instance.product.id)
        serialized = ProductViewSerializer(product,context = {"request": request}).data
        return serialized


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "total_amount", "cart_items"]


class PurchaseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseItems
        fields = ["id", "purchase", "product", "quantity", "price"]




class PurchaseAmountSerializer(serializers.ModelSerializer):
    tax_amount = serializers.IntegerField()
    payment_method = serializers.CharField()

    class Meta:
        model = PurchaseAmount
        fields = ["id", "total_amount", "tax_amount", "final_amount", "payment_method"]


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'email']  # Add other fields as needed

# class PurchaseAmountSerializer(serializers.ModelSerializer):
#     tax_amount = serializers.IntegerField()
#     payment_method = serializers.CharField()
#     user = UserSerializer()  # Include the user information using UserSerializer

#     class Meta:
#         model = PurchaseAmount
#         fields = ['id', 'total_amount', 'tax_amount', 'final_amount', 'payment_method', 'user']


class ViewPurchaseDeatils(serializers.ModelSerializer):
    class Meta:
        model = PurchaseItems
        fields = ["id", "product", "quantity", "price"]


class PurchaseSerializer(serializers.ModelSerializer):
    address = models.ForeignKey(
        "accounts.Address", on_delete=models.CASCADE, blank=True, null=True
    )


class PurchaseItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseItems
        fields = ("id", "product")

    def get_product(self, instance):
        return ProductViewSerializer(instance.product).data


class OrderSerializer(serializers.ModelSerializer):
    purchase_items = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    invoice_no = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Purchase
        fields = (
            "id",
            "total_amount",
            "created_at",
            "invoice_no",
            "status",
            "user",
            "purchase_items",
        )

    def get_purchase_items(self, instance):
        instances = PurchaseItems.objects.filter(purchase=instance)
        serialized = PurchaseItemSerializer(instances, many=True)
        return serialized.data  # Access the serialized data

    def get_user(self, instance):
        user = instance.user.username
        return user

    def get_created_at(self, instance):
        # Assuming created_at is a DateTimeField in your model
        formatted_date = instance.created_at.strftime("%b %d, %Y %I:%M %p")
        return formatted_date

    def get_invoice_no(self, instance):
        if Invoice.objects.filter(purchase=instance):
            invoice = Invoice.objects.get(purchase=instance)
            return invoice.invoice_no
        else:
            return 0

    def get_status(self, instance):
        print(instance.status, "_______________________________")
        purchase_log = PurchaseLogs.objects.filter(purchase=instance).latest(
            "created_at"
        )
        if PurchaseStatus.objects.filter(pk=purchase_log.status.id).exists():
            purchase_status = PurchaseStatus.objects.get(pk=purchase_log.status.id)
            serialized = PurchaseStatusSerializer(purchase_status).data
        return serialized


class PurchaseGraphItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseItems
        fields = ["product", "quantity", "attribute", "price"]


class PurchaseGraphSerializer(serializers.ModelSerializer):
    purchase_items = PurchaseGraphItemsSerializer(many=True, read_only=True)

    class Meta:
        model = Purchase
        fields = ["id", "user", "address", "total_amount", "status", "purchase_items"]


class PurchaseStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseStatus
        fields = ("id", "status", "description", "order_id")


class ProductPurchaseLogSerializer(serializers.Serializer):
    # status = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseLog
        fields = ("id", "description", "log_status")

    # def get_status(self, instance):
    #     purchase_status = PurchaseStatus.objects(id=instance.status.id)
    #     serialized = PurchaseStatusSerializer(
    #         purchase_status,
    #     ).data
    #     return serialized


class RefferalSerializer(serializers.ModelSerializer):
    referred_by = serializers.SerializerMethodField()
    referred_to = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    referral_link = serializers.SerializerMethodField()
    total_earning = serializers.SerializerMethodField()

    class Meta:
        model = Referral
        fields = (
            "id",
            "referred_by",
            "referred_to",
            "product",
            "referral_amount",
            "refferal_status",
            "referral_link",
            "total_earning",
        )

    def get_referred_by(self, instance):
        username = instance.referred_by.username
        return username

    def get_referred_to(self, instance):
        username = instance.referred_to.username
        return username

    def get_product(self, instance):
        name = instance.product.name
        return name

    def get_referral_link(self, instance):
        url = "https://youngsta-web.vercel.app/products/"
        product_code = str(instance.product.id)
        profile = UserProfile.objects.get(user=instance.referred_by)
        referal_code = profile.refferal_code
        referral_link = url + product_code + "/" + str(referal_code)
        return referral_link

    def get_total_earning(self, instance):
        total_referral_amount = Referral.objects.filter(
            referred_by=instance.referred_by, product=instance.product
        ).aggregate(total_referral_amount=Sum("referral_amount"))[
            "total_referral_amount"
        ]
        return total_referral_amount


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    customer_details = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()

    # product_details = serializers.SerializerMethodField()

    class Meta:
        model = Purchase
        fields = (
            "id",
            "created_at",
            "status",
            "total_amount",
            "customer_details",
            "invoice_no",
            "address",
            "invoice_no"
        )



    def get_status(self, instance):
        if PurchaseLog.objects.filter(Purchases=instance).exists():
            status_instance = PurchaseLog.objects.filter(Purchases=instance).latest(
                "created_at"
            )
            status = status_instance.log_status
        else:
            status = "Pending"
        return status

    def get_address(self, instance):
        address = AddressSerializer(instance.address).data
        return address

    def get_customer_details(self, instance):
        user = UserProfile.objects.get(user=instance.user)
        customer_details = {
            "name": f"{user.first_name} {user.last_name}",
            "phone": f"{user.country_code} {user.phone_number}",
        }
        return customer_details



class TransactionListSerializer(serializers.ModelSerializer):
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ("id", "amount", "credit", "created_at", "user_details")

    def get_user_details(self, instance):
        user_profile = {
            "name": f"{instance.user.last_name} {instance.user.last_name}",
            "phone_number": instance.user.phone_number,
        }
        return user_profile


class PurchaseItemSerializer(serializers.ModelSerializer):
    product_details = serializers.SerializerMethodField()
    # order_data = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseItems
        fields = ("id", "product_details", "quantity", "attribute", "price","is_cancelled", "is_returned")

    def get_product_details(self, instance):

        if ProductImages.objects.filter(product=instance.product, thumbnail=True).exists():
            thumbnail = ProductImages.objects.filter(
                product=instance.product, thumbnail=True
            ).latest("created_at")
            product_detail = {
                "name": instance.product.name,
                "selling_price": instance.product.selling_price,
                "thumbnail": thumbnail.image,
            }
            return product_detail
        return None

    # def get_order_data(self,instance):
    #     try:
    #         show_purchase = self.context.get("show_purchase")
    #         show_purchase = ast.literal_eval(show_purchase) if show_purchase in ["True","False"] else None

    #         if show_purchase:
    #             return OrderSerializer(instance.purchase).data
    #         return None
    #     except Exception as e:
    #         return str(e)

class ReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Return
        fields = "__all__"


class ReturnSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    customer_details = serializers.SerializerMethodField()
    invoice_no = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    # product_details = serializers.SerializerMethodField()

    class Meta:
        model = Return
        fields = (
            "id",
            "created_at",
            "status",
            "total_amount",
            "customer_details",
            "invoice_no",
            "address",
        )



    def get_status(self, instance):
        return "Accepted"

    def get_address(self, instance):
        address = AddressSerializer(instance.purchase_item.purchase.address).data
        return address

    def get_customer_details(self, instance):
        user = UserProfile.objects.get(user=instance.purchase_item.purchase.user)
        customer_details = {
            "name": f"{user.first_name} {user.last_name}",
            "phone": f"{user.country_code} {user.phone_number}",
        }
        return customer_details
    
    def get_total_amount(self, instance):
        total_amount = instance.purchase_item.price
        return total_amount

    def get_invoice_no(self, instance):
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    

class SourcesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sources
        fields = ["id","name"]