from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

from django.db import transaction
import traceback
from .serializers import *
from api.v1.main.decorater import *
from api.v1.main.functions import *
from products.models import *




@api_view(["POST"])
def add_to_wishlist(request,pk):
    try:
        user = request.user
        if Product.objects.filter(pk=pk).exists():
            product = Product.objects.get(pk=pk)
            if not WishlistItem.objects.filter(user=user, product=product).exists():
                wishlist = WishlistItem.objects.create(
                    user=user,
                    product = product
                )
                response_data = {
                    "StatusCode":6000,
                    "data":{
                        "message":"succesfully added to wishlist"
                    }
                }
            else:
                response_data = {
                    "StatusCode":6001,
                    "data":{
                        "message":"already in wishlist"
                    }
                }
        else:
            response_data = {
                "StatusCode":6001,
                "data":{
                    "message":"product not found"
                }
            }
        
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
    return Response({'app_data': response_data}, status=status.HTTP_400_BAD_REQUEST)




@api_view(["PUT", "PATCH"])
def edit_wishlist_item(request, pk):
    try:
        wishlist_item = WishlistItem.objects.get(pk=pk)
        serializer = WishlistItemSerializer(wishlist_item, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            response_data = {
                "StatusCode": 6000,
                "data": serializer.data,
                "message": "Wishlist item updated successfully"
            }
            return Response({'app_data': response_data}, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "data": serializer.errors,
                "message": "Invalid data"
            }
    except WishlistItem.DoesNotExist:
        response_data = {
            "StatusCode": 6004,
            "message": "Wishlist item does not exist"
        }
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
    return Response({'app_data': response_data}, status=status.HTTP_400_BAD_REQUEST)



@api_view(["DELETE"])
def delete_wishlist_item(request, pk):
    try:
        user = request.user
        print(user.username)
        if WishlistItem.objects.filter(pk=pk).exists():
            wishlist_item = WishlistItem.objects.get(pk=pk)
            wishlist_item.delete()
            response_data = {
                "StatusCode": 200,
                "message": "Wishlist item deleted successfully"
            }
        else:
            response_data={
                "StatusCode":6001,
                "data":{
                    "message":"wishlist item not found"
                }
            }
    except WishlistItem.DoesNotExist:
        response_data = {
            "StatusCode": 404,
            "message": "Wishlist item does not exist"
        }
    except Exception as e:
        response_data = {
            "StatusCode": 500,
            "message": f"An error occurred: {str(e)}"
        }

    return Response({'app_data': response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
def view_wishlist(request):
    try:
        user = request.user
        print(user.username)
        wishlist_items = WishlistItem.objects.filter(user=user)
        serializer = WishlistItemSerializer(wishlist_items, many=True)
        
        
        response_data = {
            "StatusCode": 200,
            "data": serializer.data,
            "message": "Wishlist items retrieved successfully"
        }
        return Response({'app_data': response_data}, status=status.HTTP_200_OK)
    
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
        return Response({'app_data': response_data}, status=status.HTTP_400_BAD_REQUEST)



# ---------cart view--------------







@api_view(["POST"])
def add_to_cart(request, pk):
    try:
        user = request.user
        if Product.objects.filter(pk=pk).exists():
            product = Product.objects.get(pk=pk)

            attribute = Attribute.objects.filter(product_varient__product=product).first()
            if attribute and attribute.quantity > 0:
                cart, created = Cart.objects.get_or_create(user=user)
                
                if not CartItem.objects.filter(cart=cart, product=product).exists():
                    cart_item = CartItem.objects.create(
                        cart=cart,
                        product=product,
                        price=product.price  # Set the price here based on your logic
                    )
                    cart.update_total_amount()  # Update the total amount
                    response_data = {
                        "StatusCode": 6000,
                        "data": {
                            "message": "Successfully added to cart"
                        }
                    }
                else:
                    response_data = {
                        "StatusCode": 6001,
                        "data": {
                            "message": "Already in cart"
                        }
                    }
            else:
                response_data = {
                    "StatusCode": 6002,
                    "data": {
                        "message": "Product out of stock"
                    }
                }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "message": "Product not found"
                }
            }

    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
    return Response({'app_data': response_data}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
def remove_from_cart(request, pk):
    try:
        user = request.user
        if Product.objects.filter(pk=pk).exists():
            product = Product.objects.get(pk=pk)
            cart = Cart.objects.get(user=user)

            try:
                cart_item = CartItem.objects.get(cart=cart, product=product)
                cart_item.delete()
                response_data = {
                    "StatusCode": 6000,
                    "data": {
                        "message": "Successfully removed from cart"
                    }
                }
            except CartItem.DoesNotExist:
                response_data = {
                    "StatusCode": 6002,
                    "data": {
                        "message": "Item does not exist in the cart"
                    }
                }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "message": "Product not found"
                }
            }
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }

    return Response({'app_data': response_data}, status=status.HTTP_200_OK)



@api_view(["GET"])
def view_cart_items(request):
    try:
        user = request.user
        cart_items = CartItem.objects.filter(cart__user=user)
        
        if not cart_items:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "message": "Cart is empty"
                }
            }
        else:
            serializer = CartItemSerializer(cart_items, many=True)
            response_data = {
                "StatusCode": 6000,
                "data": {
                    "cart_items": serializer.data
                }
            }
        
        return Response({'app_data': response_data}, status=status.HTTP_200_OK)
    
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
        return Response({'app_data': response_data}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(["PUT"])
def edit_cart_item(request, pk):
    try:
        user = request.user
        if Product.objects.filter(pk=pk).exists():
            product = Product.objects.get(pk=pk)
            cart = Cart.objects.get(user=user)

            try:
                cart_item = CartItem.objects.get(cart=cart, product=product)
                new_quantity = request.data.get('quantity')  # Get the new quantity from the request data
                
                # Update the quantity if a new value is provided and it's greater than 0
                if new_quantity and int(new_quantity) > 0:
                    cart_item.quantity = new_quantity
                    cart_item.save()

                    response_data = {
                        "StatusCode": 6000,
                        "data": {
                            "message": "Quantity updated successfully"
                        }
                    }
                else:
                    response_data = {
                        "StatusCode": 6003,
                        "data": {
                            "message": "Invalid quantity provided"
                        }
                    }
            except CartItem.DoesNotExist:
                response_data = {
                    "StatusCode": 6002,
                    "data": {
                        "message": "Item does not exist in the cart"
                    }
                }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "message": "Product not found"
                }
            }
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }

    return Response({'app_data': response_data}, status=status.HTTP_200_OK)


@api_view(["POST"])
def purchase_items(request):
    response_data = {}  
    try:
        user = request.user
        print(user)

        try:
            cart = Cart.objects.get(user=user)
            print(cart)
        except Cart.DoesNotExist:
            response_data = {
                "status": 6001,
                "message": "Cart not found",
            }
            return Response({'app_data': response_data}, status=status.HTTP_200_OK)

        total_amount = cart.total_amount
        print(total_amount)
        serializer = PurchaseAmountSerializer(data=request.data)
        if serializer.is_valid():
            payment_method = request.data["payment_method"]
            tax_amount = int(request.data["tax_amount"])
           
            #final amount is calculated
            final_amount = total_amount + tax_amount
            purchase_amount = PurchaseAmount.objects.create(
                user=user,
                total_amount=total_amount,
                tax=tax_amount,
                final_amount=final_amount,
                payment_method=payment_method,
               
            )
            purchase_log = PurchaseLog.objects.create(
                Purchases = purchase_amount
            )
            purchase = Purchase.objects.create(
                user = user,
                total_amount = total_amount
            )

            for cart_item in cart.cart_items.all():
                purchase_item = PurchaseItems.objects.create(
                    purchase=purchase, 
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.price,
                   
                )
                try:
                    attribute = Attribute.objects.get(product_varient__product=cart_item.product)
                    attribute.quantity -= cart_item.quantity
                    attribute.save()
                except Attribute.DoesNotExist:
                    response_data = {
                        "status": 6001,
                        "message": "Attribute does not exist"
                    }
            # Clear the user's cart after the purchase
            cart.cart_items.all().delete()
            cart.delete()
            response_data = {
                "status": 6000,
                "message": "Success",
                "data": {
                    "user": user.username,  
                    "total": total_amount,
                    "tax_amount": tax_amount,
                    "Final Amount": final_amount,
                    "payment_method": payment_method,
                }
            }
        else:
            response_data = {
            "status": 6001,
                "message": "Serializer validation failed",
                "errors": serializer.errors
            }
            return Response({'app_data': response_data}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        response_data = {
            "status": 6001,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }

    return Response({'app_data': response_data}, status=status.HTTP_200_OK)


        
