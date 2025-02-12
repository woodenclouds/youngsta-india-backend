import requests
import json
from django.conf import settings
from accounts.models import *
from activities.models import *
from payments.models import *
from accounts.models import Address
from decimal import Decimal


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
    

def createOrder(purchase:Purchase):
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
            "sku": product.product_sku if product.product_sku else "SKU123Fg" ,  # Replace with actual SKU if available
            "units": quantity,
            "selling_price": float(product.selling_price),
        }
        items.append(item)

    payload = {
        "order_id": str(purchase.id),  # Convert UUID to string
        "order_date": purchase.created_at.isoformat(),  # Convert datetime to string
        "billing_customer_name": f"{address.first_name} {address.last_name}",
        "billing_last_name": f"{address.last_name}",
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
        
        purchase.SR_order_id = order_response.get('order_id')
        purchase.SR_shipment_id = order_response.get('shipment_id')
        purchase.save()
        
        bill_api = "https://apiv2.shiprocket.in/v1/external/orders/print/invoice"
        headers = {
            'Authorization': f'Bearer {generateAccessShiprocket()}',
            'Content-Type': 'application/json'
        }
        payload = {
            "ids": [order_response["order_id"]],
        }
        bill_response = requests.post(bill_api, headers=headers, json=payload)
        print(bill_response,"____bill response")
        
        print(f"Order created successfully: {order_response}")
        return {
            "bill_response":bill_response,
            "order_response":order_response,
        }
    else:
        print(f"Failed to create order. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return response.text


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
    total_tax = 0
    total_price_excluding_tax = 0

    for item in order_items:
        product = Product.objects.filter(id=item.product.id).first()
        if product:
            total_price = item.quantity * product.selling_price
            tax =  Decimal('0.05') * total_price
            cgst =  Decimal('0.05') * total_price/2
            sgst =  Decimal('0.05') * total_price/2
            price_excluding_tax = product.price-tax/item.quantity
            product_details.append({
                'product_name': product.name,
                'product_description': product.description,
                'similar_code':product.similar_code,
                'quantity': item.quantity,
                'price_excluding_tax': f"{price_excluding_tax:.2f}",
                'CGST': f"{cgst:.2f}",
                'SGST': f"{sgst:.2f}",
                'gst': product.gst_price,
                'total_price': total_price,           
            })
            total_price_excluding_tax += price_excluding_tax * item.quantity
            grand_total += total_price
            total_products += item.quantity 
            total_tax += tax


        # --- Order Details ---
    invoice = Invoice.objects.filter(purchase__id=order.id).first()
    shipping_charge = getattr(order, 'shipping_charge', 0)      
    order_details = {
        'order_id': str(order.invoice_no),
        'ordered_date': order.created_at.strftime("%d %b %Y"),
        'invoice_number': order.invoice_no,  
        'invoice_date': invoice.issued_at.strftime("%d %b %Y") if invoice and invoice.issued_at else "----",
        'total_products': total_products,
        'total_cgst': f"{total_tax/2:.2f}",
        'total_sgst': f"{total_tax/2:.2f}",
        'grand_total': f"{grand_total:.2f}",
        'total_price_excluding_tax':f"{total_price_excluding_tax:.2f}",
        'shipping_charge': f"{shipping_charge:.2f}" if shipping_charge else "0"
    }
    # --- Billing Details ---
    billing_details = []

    if ( billing_address := Address.objects.filter(id=order.address.id, is_deleted=False)).exists():
        billing_address = billing_address.first()

        billing_details = {
            'billing_name': billing_address.first_name if billing_address.first_name else "",
            'billing_address': billing_address.address if billing_address.address else "",
            'billing_street': billing_address.street if billing_address.street else "",
            'billing_city': billing_address.city if billing_address.city else "",
            'billing_pincode': billing_address.post_code if billing_address.post_code else "",
            'billing_state': billing_address.state if billing_address.state else "",
            'billing_country': billing_address.country if billing_address.country else "",
            'billing_phone': billing_address.phone if billing_address.phone else "",
        }
  
    # Combine all details into a dictionary
    invoice_data = {
        'order_details': order_details,
        'billing_details': billing_details,
        'product_details': product_details,
    }
    
    return invoice_data

    

def getTrackingDetailsByShipmentID(shipmentId):
    api = f"https://apiv2.shiprocket.in/v1/external/courier/track/shipment/{shipmentId}"
    token = generateAccessShiprocket()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(api, headers=headers)
        response_data = response.json()
            
        return response_data
    except Exception as e:
        return e