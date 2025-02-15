import json

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
from api.v1.accounts.functions import send_otp_email

from cashfree_pg.models.create_order_request import CreateOrderRequest
from cashfree_pg.api_client import Cashfree
from cashfree_pg.models.customer_details import CustomerDetails


stripe.api_key = settings.STRIPE_SECRET_KEY

Cashfree.XClientId = settings.CASHFREE_APP_ID
Cashfree.XClientSecret = settings.CASHFREE_SECRET
Cashfree.XEnvironment = Cashfree.XSandbox
x_api_version = "2023-08-01"

def create_cashfree_order():
    customerDetails = CustomerDetails(customer_id="123", customer_phone="9999999999")
    createOrderRequest = CreateOrderRequest(order_amount=1, order_currency="INR", customer_details=customerDetails)
    try:
        api_response = Cashfree().PGCreateOrder(x_api_version, createOrderRequest, None, None)
        return api_response.data
    except Exception as e:
        return str(e)


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
        address = request.data.get("address")
        coupon_code = request.data.get("coupon_code")
        use_wallet_balance = request.data.get("use_wallet_balance")
        
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

                # discount calculations
                # wallet_discount = cart.wallet_discount or 0
                coupen_offer = cart.coupen_offer or 0
                
                if coupon_code and cart.coupon_code == coupon_code:
                    total_price = total_price - coupen_offer
                
                    if (cart.product_total - coupen_offer) != total_price:
                        response_data = {
                            "StatusCode": 6001,
                            "data": {
                                "title": "An error occurred",
                                "status_code": 'Something went wrong',
                                "amount":f'{cart.product_total} - {coupen_offer} - {total_price}'
                            },
                        }
                        return Response({"app_data": response_data}, status=status.HTTP_200_OK)

                # with transaction.atomic():
                purchase = Purchase.objects.create(
                    user=user,
                    total_amount=total_price,
                    address = address,
                    is_deleted = True
                )
                
                if coupon_code and cart.coupon_code == coupon_code:
                    purchase.coupon_code = coupon_code
                    purchase.coupon_discount = coupen_offer
                    purchase.total_without_discount = cart.product_total
                    purchase.save()

                for item in cart_items:
                    PurchaseItems.objects.create(
                        purchase=purchase,
                        product=item.product,
                        quantity=item.quantity,
                        attribute= item.attribute,
                        price=item.price,
                    )

                    if item.referral_code and UserProfile.objects.filter(refferal_code=item.referral_code).exists():
                        user_refered = UserProfile.objects.get(refferal_code=item.referral_code)
                        if not Referral.objects.filter(product=item.product,referred_by = user_refered.user,referred_to = customer_profile.user).exists():
                            Referral.objects.create(
                                product = item.product,
                                referred_by = user_refered.user,
                                referred_to = customer_profile.user,
                                referral_amount = item.product.referal_Amount,
                                order = purchase,
                                refferal_status='pending',
                                is_paid = False
                            ) 
                        # wallet = Wallet.objects.get(user=user_refered)
                        # wallet.balance += item.product.referal_Amount
                        # wallet.save()

                # cart.total_amount = 0
                # cart.coupen_offer = 0
                # cart.coupon_code = ''
                # cart.product_total = 0
                # cart.save()
                cash_free_args = {
                    "request": request,
                    "instance": purchase,
                    "customer_profile": customer_profile,
                }
                cash_free_create_order_response, payment_link_status,headers = create_cash_free_order(
                    cash_free_args
                )
                # response = create_cashfree_order()
                # response_data = {
                #         "StatusCode": 6001,
                #         "data": {
                #             "title": "An error occurred",
                #             "status_code": response
                #         },
                #     }
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
                            "use_wallet_balance":use_wallet_balance
                        },
                    }
                else:
                    response_data = {
                        "StatusCode": 6001,
                        "data": {
                            "title": "An error occurred",
                            "status_code": cash_free_create_order_response.json(),
                            "headers":headers
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
        request_url = f"{settings.CASH_FREE_END_POINT}/orders/{purchase.id}"
        headers = {
            "accept": "application/json",
            "x-api-version": "2023-08-01",
            "x-client-id": settings.CASHFREE_APP_ID,
            "x-client-secret": settings.CASHFREE_SECRET,
        }
        order_status_response = requests.get(request_url, headers=headers)
        # print(order_status_response.json())
        # send_otp_email("safwan.woodenclouds@gmail.com",str(order_status_response.json()))
        if order_status_response.status_code == 200:
            order_status = order_status_response.json()
            # user = request.user
            user_profile = UserProfile.objects.get(user=purchase.user)
            # send_otp_email("safwan.woodenclouds@gmail.com",str(order_status))
            if order_status["order_status"] == "ACTIVE":
                purchase.status = "Pending"
                purchase.is_deleted = False
                purchase.save()
                purchase_item = PurchaseItems.objects.filter(purchase=purchase)
                # referrals
                for item in purchase_item:
                    attribute = item.attribute
                    attribute.quantity -= item.quantity
                    attribute.save()
                    
                if purchase.referrals.filter(is_deleted=False):
                    for referral in purchase.referrals.filter(is_deleted=False):
                        WalletTransaction.objects.create(
                            user=referral.referred_by.userprofile,
                            amount=referral.referral_amount,
                            transaction_status='processing',
                            transaction_description=f"Reward for referring product to {user_profile.first_name}"
                        )
                    
                current_time = datetime.datetime.now().date()
                invoice = Invoice.objects.create(
                    invoice_no = "",
                    issued_at = current_time,
                    customer_name = f"{user_profile.first_name} {user_profile.last_name}",
                    total_amount = purchase.total_amount,
                    purchase = purchase,
                )
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
                cart.total_amount = 0
                cart.coupen_offer = 0
                cart.coupon_code = ''
                cart.product_total = 0
                cart.save()
                cart_items = CartItem.objects.filter(cart=cart)
                cart_items.delete()
                url = "https://youngsta.in/my-account/orders?action=payment_success"
                return redirect(url)
            else:
                url = f"https://youngsta.in/my-account/orders?action=payment_failed"
                return redirect(url)
        else:
            url = f"https://youngsta.in/my-account/orders?action=payment_failed"
            return redirect(url)
    else:
        url = f"https://youngsta.in/my-account/orders?action=payment_failed"
        return redirect(url)

