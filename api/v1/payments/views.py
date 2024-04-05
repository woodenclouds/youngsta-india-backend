from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
import stripe
import razorpay

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
