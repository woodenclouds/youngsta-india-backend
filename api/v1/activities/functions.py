import requests
import json
from django.conf import settings
from accounts.models import *
from activities.models import *



def generateAccessShiprocket():
    # Access Shiprocket API
    api = "https://apiv2.shiprocket.in/v1/external/auth/login"
    headers = {
        'Content-Type': 'application/json'
    }
    print(settings.SHIPROCKET_EMAIL,settings.SHIPROCKET_PASSWORD)
    payload = {
        "email": "anooj.woodenclouds@gmail.com",  
        "password": "#fhMpSm.W4wwy.n"        
    }
    payload_json = json.dumps(payload)
    response = requests.post(api, headers=headers, json=payload)
    
    if response.status_code == 200:
        token = response.json().get('token')
        print(f"Access token: {token}")
        return token
    else:
        print(f"Failed to get access token. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return None
    

def createOrder(purchase):
    api = "https://apiv2.shiprocket.in/v1/external/orders/create/adhoc"
    headers = {
        'Authorization': f'Bearer {generateAccessShiprocket()}',
        'Content-Type': 'application/json'
    }
    
    address = purchase.address
    user_profile = UserProfile.objects.get(user=purchase.user)
    purchase_items = PurchaseItems.objects.filter(purchase=purchase)
    
    items = []
    weight = 0
    length = 0
    breadth = 0
    height = 0

    for purchase_item in purchase_items:
        product = purchase_item.product
        quantity = purchase_item.quantity
        
        # Weight
        weight += float(product.weight) * quantity
        
        # Dimensions
        if float(product.length) > length:
            length = float(product.length)
        breadth += float(product.width) * quantity
        height += float(product.height) * quantity

        item = {
            "name": product.name,
            "sku": "SKU123Fg",  # Replace with actual SKU if available
            "units": quantity,
            "selling_price": float(product.selling_price),
        }
        items.append(item)

    payload = {
        "order_id": str(purchase.id),  # Convert UUID to string
        "order_date": purchase.created_at.isoformat(),  # Convert datetime to string
        "billing_customer_name": f"{address.first_name} {address.last_name}",
        "billing_address": address.address,
        "billing_city": address.city,
        "billing_pincode": address.post_code,
        "billing_state": address.state,
        "billing_country": "India",
        "billing_phone": address.phone,
        "shipping_is_billing": True,
        "order_items": items,
        "payment_method": "online",
        "shipping_charges": 50,
        "giftwrap_charges": 0,
        "transaction_charges": 0,
        "total_discount": 0,
        "sub_total": float(purchase.total_amount),
        "length": length,
        "breadth": breadth,
        "height": height,
        "weight": weight
    }

    response = requests.post(api, headers=headers, json=payload)
    if response.status_code == 200:
        order_response = response.json()
        print(f"Order created successfully: {order_response}")
        return order_response
    else:
        print(f"Failed to create order. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return None


def getServiceAvailability(cart, pin_code):
    api = "https://apiv2.shiprocket.in/v1/external/courier/serviceability/"
    token = generateAccessShiprocket()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    cart_items = CartItem.objects.filter(cart=cart)
    weight = 0
    length = 0
    breadth = 0
    height = 0

    for item in cart_items:
        product = item.product
        quantity = item.quantity
        
        # Weight
        weight += float(product.weight) * quantity
        
        # Dimensions
        if float(product.length) > length:
            length = float(product.length)
        breadth += float(product.width) * quantity
        height += float(product.height) * quantity

    payload = {
        "pickup_postcode": "682019",  # Assuming `purchase` has these attributes
        "delivery_postcode": pin_code,
        "weight": weight,
        "length": length,
        "breadth": breadth,
        "height": height,
        "cod": False  # Assuming COD is false
    }
    
    response = requests.get(api, headers=headers, json=payload)
    response_data = response.json()
    
    if response.status_code == 200:
        return response_data
    else:
        raise Exception(f"Failed to get service availability: {response_data,token}")
