import requests
import json
from django.conf import settings
from accounts.models import *
from activities.models import *
from payments.models import *
from accounts.models import Address


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
        bill_api = "https://apiv2.shiprocket.in/v1/external/orders/print/invoice"
        headers = {
            'Authorization': f'Bearer {generateAccessShiprocket()}',
            'Content-Type': 'application/json'
        }
        payload = {
            "ids": [order_response["order_id"]],
        }
        bill_response = requests.post(api, headers=headers, json=payload)
        print(bill_response,"____bill response")
        
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


def get_invoice_data(pk):
    
    order = Purchase.objects.filter(id=pk, is_deleted=False).first()   
    if not order:
        return None  
    current_date = timezone.now().strftime('%Y%m%d')
    
    # --- Product Details ---

    order_items = PurchaseItems.objects.filter(purchase__id=order.id)
    product_details = []
    grand_total = 0
    total_products = 0

    for item in order_items:
        product = Product.objects.filter(id=item.product.id).first()
        if product:
            total_price = item.quantity * product.selling_price
            product_details.append({
                'product_name': product.name,
                'product_description': product.description,
                'product_code':product.product_code,
                'quantity': item.quantity,
                'price': product.price,
                # 'tax': product.tax,
                'gst': product.gst_price,
                'total_price': total_price,           
            })
            grand_total += total_price
            total_products += item.quantity 

        # --- Order Details ---
    invoice = Invoice.objects.filter(purchase__id=order.id).first()

    order_details = {
        'order_id': str(order.id),
        'ordered_date': order.created_at.strftime("%d %b %Y"),
        'invoice_number': order.invoice_no,  
        'invoice_date': invoice.issued_at.strftime("%d %b %Y"),
        'total_products': total_products,
        'grand_total': f"{grand_total:.2f}",
    }

    # --- Billing Details ---
    billing_details = []

    if ( billing_address := Address.objects.filter(id=order.address.id, is_deleted=False)).exists():
        billing_address = billing_address.first()

        billing_details = {
            'billing_name': billing_address.first_name,
            'billing_address': billing_address.address,
            'billing_street': billing_address.street,
            'billing_city': billing_address.city,
            'billing_pincode': billing_address.post_code,
            'billing_state': billing_address.state,
            'billing_country': billing_address.country,
            'billing_phone': billing_address.phone,
        }
  
    # Combine all details into a dictionary
    invoice_data = {
        'order_details': order_details,
        'billing_details': billing_details,
        'product_details': product_details,
    }
    
    return invoice_data

    