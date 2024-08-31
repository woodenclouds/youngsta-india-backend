from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
import stripe
import razorpay
from rest_framework import status
from activities.models import *
from accounts.models import *
from payments.models import *
from .functions import *
from django.shortcuts import get_object_or_404, redirect


stripe.api_key = settings.STRIPE_SECRET_KEY


# def create_checkout_session(
#     currency="usd",
#     purchase_id="",
#     unit_amount=2000,
#     quantity=1,
#     mode="payment",
#     success_url="/success/",
#     cancel_url="/cancel/",
# ):
#     try:
#         session_params = {
#             "payment_method_types": ["card"],
#             "line_items": [
#                 {
#                     "price_data": {
#                         "currency": currency,
#                         "product_data": {
#                             "name": "Your Product",
#                         },
#                         "unit_amount": unit_amount,  # amount in cents
#                     },
#                     "quantity": quantity,
#                 },
#             ],
#             "mode": mode,
#             "success_url": success_url,
#             "cancel_url": cancel_url,
#             "metadata": {
#                 "purchase_id": purchase_id,
#             },
#         }

#         session = stripe.checkout.Session.create(**session_params)
#         return {"id": session.id}
#     except Exception as e:
#         return {"error": str(e)}


def create_checkout_session(amount, currency="INR"):
    try:
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        order_data = {
            "amount": amount * 100,
            "currency": currency,
            "receipt": "your_order_id",
            "payment_capture": 1,
        }
        response = client.order.create(data=order_data)
        order_id = response.get("id")
        return {"order_id": order_id, "amount": amount}
    except Exception as e:
        return {"error": str(e)}


@api_view(["POST"])
def create_order(request):
    try:
        user = request.user
        customer_profile = UserProfile.objects.get(user=user)
        address = request.data["address"]
        if not address:
            response_data = {
                "StatusCode":6001,
                "data":{
                    "message":"address is required"
                }
            }
            return Response({"app_data": response_data}, status=status.HTTP_200_OK)
        if not Address.objects.filter(pk=address).exists():
            response_data = {
                "StatusCode":6001,
                "data":{
                    "message":"address not found"
                }
            }
            return Response({"app_data": response_data}, status=status.HTTP_200_OK)
        if Cart.objects.filter(user=user).exists():
            cart = Cart.objects.get(user=user)

            if CartItem.objects.filter(cart=cart).exists():
                cart_items = CartItem.objects.filter(cart=cart)
                address = Address.objects.get(pk=address)
                total_price = sum(item.price for item in cart_items)
                # with transaction.atomic():
                purchase = Purchase.objects.create(
                    user=user,
                    total_amount=total_price,
                    address = address,
                    is_deleted = True
                )
                for item in cart_items:
                    purchase_item = PurchaseItems.objects.create(
                        purchase=purchase,
                        product=item.product,
                        quantity=item.quantity,
                        attribute= item.attribute,
                        price=item.price,
                    )
                    if item.referral_code:
                        if  UserProfile.objects.filter(refferal_code=item.referral_code).exists():
                            user_refered = UserProfile.objects.get(refferal_code=item.referral_code)
                            refferal_instance = Referral.objects.create(
                                product = item.product,
                                referred_by = user_refered.user,
                                referred_to = customer_profile.user,
                                referral_amount = item.product.referal_Amount,
                                order = purchase,
                                is_paid = False
                            )
                            wallet = Wallet.objects.get(user=user_refered)
                            wallet.balance += item.product.referal_Amount
                            wallet.save()
                cart.total_amount = 0
                cart.coupen_offer = 0
                cart.coupon_code = ''
                cart.product_total = 0
                cart.save()
                cash_free_args = {
                    "request": request,
                    "customer_profile": customer_profile,
                    "instance": purchase,
                }
                cash_free_create_order_response, payment_link_status = create_cash_free_order(
                    cash_free_args
                )
                if cash_free_create_order_response.status_code == 200 and payment_link_status:
                    cash_free_create_order_response = cash_free_create_order_response.json()

                    response_data = {
                        "StatusCode": 6000,
                        "data": {
                            "title": "Success",
                            "purchase": purchase.pk,
                            "payment_url": cash_free_create_order_response["link_url"],
                            "link_expiry_time": cash_free_create_order_response[
                                "link_expiry_time"
                            ],
                        },
                    }
                else:
                    response_data = {
                        "StatusCode": 6001,
                        "data": {
                            "title": "An error occurred",
                            "status_code": cash_free_create_order_response,
                        },
                    }
            else:
                response_data = {
                    "StatusCode":6001,
                    "data":{
                        "message":"no items in the cart"
                    }
                }
        else:
            response_data = {
                "StatusCode":6001,
                "data":{
                    "message":"cart not found"
                }
            }
    except Exception as e:
        # transaction.set_rollback(True)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
def handle_response(request):
    purchase_id = request.GET.get("pk")
    if Purchase.objects.filter(pk=purchase_id).exists():
        purchase = Purchase.objects.get(pk=purchase_id)
        request_url = f"{settings.CASH_FREE_END_POINT}orders/{purchase.id}"
        headers = {
            "accept": "application/json",
            "x-api-version": "2023-08-01",
            "x-client-id": settings.CASHFREE_APP_ID,
            "x-client-secret": settings.CASHFREE_SECRET,
        }
        order_status_response = requests.get(request_url, headers=headers)
        print(order_status_response.json())
        if order_status_response.status_code == 200:
            order_status = order_status_response.json()
            # user = request.user
            user_profile = UserProfile.objects.get(user=purchase.user)
            if order_status["order_status"] == "ACTIVE":
                purchase.status = "Pending"
                purchase.is_deleted = False
                purchase.save()
                purchase_item = PurchaseItems.objects.filter(purchase=purchase)
                for item in purchase_item:
                    attribute = item.attribute
                    attribute.quantity -= item.quantity
                    attribute.save()
                purchase_log = PurchaseLog.objects.create(
                    Purchases=purchase,
                    log_status = "Pending"
                )
                transaction_ins = Transaction.objects.create(
                    user=user_profile,
                    amount=purchase.total_amount,
                    transaction_type="DEBIT",
                    transaction_mode="ONLINE",
                    transaction_id=purchase.pk,
                    transaction_status="SUCCESS",
                    transaction_description="Purchased from cashfree",
                )
                cart = Cart.objects.get(user=purchase.user)
                cart_items = CartItem.objects.filter(cart=cart)
                cart_items.delete()
                url = "https://youngsta.in/my-account/orders?action=payment_success"
                return redirect(url)
            else:
                url = "https://youngsta.in/my-account/orders?action=payment_failed"
                return redirect(url)
        else:
            url = "https://youngsta.in/my-account/orders?action=payment_failed"
            redirect(url)
    else:
        url = "https://youngsta.in/my-account/orders?action=payment_failed"
        redirect(url)