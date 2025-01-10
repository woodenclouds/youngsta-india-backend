
from django.conf import settings
import requests
import datetime
from django.urls import reverse
from dateutil.tz import tzoffset


x_api_version = settings.CASH_FREE_X_API_VERSION
def create_cash_free_order(cash_free_args):
    customer_profile = cash_free_args.get("customer_profile")
    request = cash_free_args.get("request")
    instance = cash_free_args.get("instance")

    customer_email = ""
    if customer_profile.email:
        customer_email = customer_profile.email

    protocol = "http://"
    if request.is_secure():
        protocol = "https://"

    web_host = request.get_host()

    # Set return url
    returnUrl = f"{protocol}{web_host}/api/v1/payments/handle-response/?pk={instance.pk}"
    print(returnUrl)

    # Create a timezone offset for IST (+05:30)
    ist_offset = tzoffset(None, 5 * 60 * 60 + 30 * 60)

    payload = {
        "order_id": f"{instance.id}",
        "order_amount": float(instance.total_amount),
        "order_currency": "INR",
        "order_expiry_time": (
            datetime.datetime.now() + datetime.timedelta(minutes=15, seconds=30)
        )
        .astimezone(ist_offset)
        .isoformat(),
        "order_meta": {"return_url": returnUrl},
        "customer_details": {
            "customer_id": f"{customer_profile.id}",
            "customer_email": f"{customer_email}",
            "customer_phone": f"{customer_profile.phone_number}",
            "customer_name": customer_profile.first_name,
        },
    }
    headers = {
        "accept": "application/json",
        "x-api-version": "2023-08-01",  # Set the correct version value here
        "content-type": "application/json",
        "x-client-id": settings.CASHFREE_APP_ID,
        "x-client-secret": settings.CASHFREE_SECRET,
    }

    create_order_url = f"{settings.CASH_FREE_END_POINT}/orders"
    print(create_order_url)
    response = requests.post(create_order_url, json=payload, headers=headers)
    print(response)
    if response.status_code == 200:
        payment_link_generation_url = f"{settings.CASH_FREE_END_POINT}/links"
        payload = {
            "customer_details": {
                "customer_id": f"{customer_profile.id}",
                "customer_email": f"{customer_email}",
                "customer_phone": f"{customer_profile.phone_number}",
                "customer_name": customer_profile.first_name,
            },
            "link_meta": {"return_url": returnUrl, "notify_url": returnUrl},
            "link_notify": {"send_sms": False},
            "link_id": f"{instance.id}",
            "link_amount": float(instance.total_amount),
            "link_currency": "INR",
            "link_purpose": f"Please pay to complete the order.",
            "link_expiry_time": (
                datetime.datetime.now() + datetime.timedelta(minutes=15, seconds=30)
            )
            .astimezone(ist_offset)
            .isoformat(),
        }
        headers = {
            "accept": "application/json",
            "x-api-version": "2023-08-01",  # Set the correct version value here
            "content-type": "application/json",
            "x-client-id": settings.CASHFREE_APP_ID,
            "x-client-secret": settings.CASHFREE_SECRET,
        }

        response = requests.post(
            payment_link_generation_url, json=payload, headers=headers
        )
        return response, True,headers
    return response, False,headers