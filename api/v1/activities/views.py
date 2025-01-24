from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.db.models.functions import TruncDay, TruncMonth
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.templatetags.static import static


from django.db import transaction
import traceback
from .serializers import *
from api.v1.main.decorater import *
from api.v1.main.functions import *
from products.models import *
from payments.models import *
from main.encryptions import *
from decimal import Decimal
from api.v1.payments.views import *
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from django.contrib.auth import authenticate
from django.db.models import Sum
from django.db.models.functions import TruncWeek,TruncMonth
from accounts.models import *
from datetime import datetime, timedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Subquery, OuterRef
from .functions import *
from marketing.models import *

from io import BytesIO
from xhtml2pdf import pisa



@api_view(["POST"])
def add_to_wishlist(request, pk):
    try:
        user = request.user
        if Product.objects.filter(pk=pk).exists():
            product = Product.objects.get(pk=pk)
            if not WishlistItem.objects.filter(user=user, product=product).exists():
                wishlist = WishlistItem.objects.create(user=user, product=product)
                response_data = {
                    "StatusCode": 6000,
                    "data": {"message": "successfully added to wishlist"},
                }
            else:
                wishlist = WishlistItem.objects.get(user=user, product=product)
                wishlist.delete()
                response_data = {
                    "StatusCode": 6000,
                    "data": {"message": "removed from wishlist"},
                }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {"message": "product not found"},
            }

    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["PUT", "PATCH"])
def edit_wishlist_item(request, pk):
    try:
        wishlist_item = WishlistItem.objects.get(pk=pk)
        serializer = WishlistItemSerializer(
            wishlist_item, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            response_data = {
                "StatusCode": 6000,
                "data": serializer.data,
                "message": "Wishlist item updated successfully",
            }
            return Response({"app_data": response_data}, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "data": serializer.errors,
                "message": "Invalid data",
            }
    except WishlistItem.DoesNotExist:
        response_data = {"StatusCode": 6004, "message": "Wishlist item does not exist"}
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
    return Response({"app_data": response_data}, status=status.HTTP_400_BAD_REQUEST)


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
                "message": "Wishlist item deleted successfully",
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {"message": "wishlist item not found"},
            }
    except WishlistItem.DoesNotExist:
        response_data = {"StatusCode": 404, "message": "Wishlist item does not exist"}
    except Exception as e:
        response_data = {"StatusCode": 500, "message": f"An error occurred: {str(e)}"}

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
def view_wishlist(request):
    try:
        user = request.user
        print(user.username)
        wishlist_items = WishlistItem.objects.filter(user=user)
        serializer = WishlistItemSerializer(wishlist_items,context = {"request":request} ,many=True)

        response_data = {
            "StatusCode": 200,
            "data": serializer.data,
            "message": "Wishlist items retrieved successfully",
        }
        return Response({"app_data": response_data}, status=status.HTTP_200_OK)

    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
        return Response({"app_data": response_data}, status=status.HTTP_400_BAD_REQUEST)


# ---------cart view--------------


@api_view(["POST"])
@permission_classes((AllowAny,))
def add_to_cart(request, pk):
    try:
        user = request.user
        attribute_id = request.data["attribute_id"]
        quantity = request.data["quantity"]
        referral_code = request.data.get("referral_code")
        if attribute_id:
            if ProductAttribute.objects.filter(pk=attribute_id).exists():
                if Product.objects.filter(pk=pk).exists():
                    product = Product.objects.get(pk=pk)
                    attribute_description = ProductAttribute.objects.get(
                        pk=attribute_id
                    )
                    if attribute_description.quantity < quantity:
                        response_data = {
                            "StatusCode": 6001,
                            "data":{
                                "message": "Requested quantity exceeds available stock"
                            }
                        }
                    cart = Cart.objects.get(user=user)
                    
                    if not CartItem.objects.filter(cart=cart, product=product).exists():
                        cart_item = CartItem.objects.create(
                            cart=cart,
                            product=product,
                            attribute=attribute_description,
                            quantity=Decimal(quantity),
                            price=product.selling_price * Decimal(quantity),
                        )
                        if referral_code:
                            cart_item.referral_code = referral_code
                            cart_item.save()
                            
                        cart.product_total += cart_item.price
                        cart.save()
                        response_data = {
                            "StatusCode": 6000,
                            "data": {"message": "Added to cart"},
                        }
                    else:
                        response_data = {
                            "StatusCode": 6001,
                            "data": {"message": "Product already exists in cart"},
                        }
                else:
                    response_data = {
                        "StatusCode": 6001,
                        "data": {"message": "Varient not exist"},
                    }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "data": {"message": "Attribute not exist with this pk"},
                }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {"message": "attribute_id is required"},
            }
    except Exception as e:
        response_data = {
            "status": 6001,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


# @api_view(["POST"])
# def add_to_cart(request, pk):
#     try:
#         user = request.user
#         if ProductVarient.objects.filter(pk=pk).exists():
#             product_varient = ProductVarient.objects.get(pk=pk)

#             attribute = VarientAttribute.objects.filter(varient=product_varient).first()
#             if attribute and attribute.quantity > 0:
#                 cart, created = Cart.objects.get_or_create(user=user)

#                 if not CartItem.objects.filter(cart=cart, product=product).exists():
#                     cart_item = CartItem.objects.create(
#                         cart=cart,
#                         product=product,
#                         price=product.price  # Set the price here based on your logic
#                     )
#                     cart.update_total_amount()  # Update the total amount
#                     response_data = {
#                         "StatusCode": 6000,
#                         "data": {
#                             "message": "Successfully added to cart"
#                         }
#                     }
#                 else:
#                     response_data = {
#                         "StatusCode": 6001,
#                         "data": {
#                             "message": "Already in cart"
#                         }
#                     }
#             else:
#                 response_data = {
#                     "StatusCode": 6002,
#                     "data": {
#                         "message": "Product out of stock"
#                     }
#                 }
#         else:
#             response_data = {
#                 "StatusCode": 6001,
#                 "data": {
#                     "message": "Product not found"
#                 }
#             }

#     except Exception as e:
#         response_data = {
#             "status": 0,
#             "api": request.get_full_path(),
#             "request": request.data,
#             "message": str(e),
#         }
#     return Response({'app_data': response_data}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def remove_from_cart(request, pk):
    try:
        cart = Cart.objects.get(user=request.user)
        if CartItem.objects.filter(pk=pk).exists():
            item = CartItem.objects.get(pk=pk)
            if item.cart == cart:
                item.delete()
                response_data = {
                    "StatusCode": 6000,
                    "data": {"data": "removed cart item succesfully"},
                }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "data": {"message": "You dont have permission"},
                }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {"message": "Cart item not found"},
            }
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


# @api_view(["GET"])
# def view_cart_items(request):
#     try:
#         user = request.user
#         if not user:
#             response_data = {
#                 "StatusCode":6001,
#                 "data":{
#                     "message":"user not found"
#                 }
#             }
#         if Cart.objects.filter(user=user).exists():
#             cart = Cart.objects.get(user=user)
#         else:
#             cart = Cart.objects.create(
#                 user = user
#             )
#         cart_items = CartItem.objects.filter(cart=cart)
#         if not cart_items:
#             response_data = {"StatusCode": 6001, "data": {"message": "Cart is empty"}}
#         else:
#             serializer = CartItemSerializer(cart_items, many=True)
#             response_data = {
#                 "StatusCode": 6000,
#                 "mead":"dscsds",
#                 "data": {"cart_items": serializer.data},
#             }

#         return Response({"app_data": response_data}, status=status.HTTP_200_OK)

#     except Exception as e:
#         response_data = {
#             "status": 0,
#             "api": request.get_full_path(),
#             "request": request.data,
#             "message": str(e),
#         }
#         return Response(
#             {"app_data": response_data}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )


@api_view(["GET"])
def get_cart(request):
    try:
        print(request.user,":user")
        if request.user is not None:  # Check if there is an authenticated user
            if Cart.objects.filter(user=request.user).exists():
                cart = Cart.objects.get(user=request.user)
                cart_items = CartItem.objects.filter(cart=cart)
                serializer = CartItemSerializer(cart_items,context={"request":request}, many=True)

                response_data = {
                    "StatusCode": 6000,
                    "message": "Cart Items",
                     "data": {
                         "total_price":cart.total_amount,
                         "discount":cart.coupen_offer,
                         "product_total":cart.product_total,
                         "cart_items": serializer.data
                         },
                }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "Cart not found",
                }
        else:
            response_data = {
                "StatusCode": 6002,
                "message": "User not authenticated",
            }
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)

@api_view(["PUT"])
def edit_cart_item(request, pk):
    try:
        user = request.user
        cart = Cart.objects.get(user=user)
        try:
            quantity = request.data["quantity"]
        except:
            quantity = None
        try:
            attribute_id = request.data["attribute_id"]
        except:
            attribute_id = None
        cart_item = CartItem.objects.filter(pk=pk, cart=cart).first()
        if cart_item:
            if quantity:
                cart_item.quantity = quantity
                cart_item.price = cart_item.product.selling_price * quantity
            if attribute_id:
                attribute = ProductAttribute.objects.get(pk=attribute_id)
                cart_item.attribute = attribute
            cart_item.save()
            cart.product_total += cart_item.price 
            cart.save()
            response_data = {
                "StatusCode": 6000,
                "data": {"message": "Updated item succesfully"},
            }
        else:
            response_data = {
                "StatusCode": 6000,
                "data": {"message": "Cart item not found or dont have permission"},
            }
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["POST"])
def purchase_items(request):
    try:
        transaction.set_autocommit(False)
        cart = Cart.objects.get(user=request.user)
        # Check if Cart Items Exist
        try:
            refferal_id = request.data["refferal_id"]
        except:
            refferal_id = None
        if CartItem.objects.filter(cart=cart).exists():
            address = Address.objects.get(pk=request.data["address"])
            cart_items = CartItem.objects.filter(cart=cart)

            # Calculate Total Price
            total_price = cart_items.aggregate(total_price=Sum("price"))["total_price"]

            # Create Purchase Object
            purchase = Purchase.objects.create(
                total_amount=total_price,
                user=request.user,
                address=address,
                status="Pending",
            )
            # Create PurchaseItems Objects
            for cart_item in cart_items:
                purchase_item = PurchaseItems.objects.create(
                    purchase=purchase,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.price,
                )
            transaction.commit()
            # Create Checkout Session
            # strape = create_checkout_session(
            #     currency="usd",
            #     purchase_id=str(purchase.id),
            #     unit_amount=2000,
            #     quantity=1,
            #     mode="payment",
            #     success_url=f"https://api.youngsta.uk/api/v1/activities/success/{purchase.id}",
            #     cancel_url="https://api.youngsta.uk/api/v1/payments/cancel/",
            # )
            order_data = create_checkout_session(total_price)

            if refferal_id:
                if Referral.objects.filter(pk=refferal_id).exists():
                    referral = Referral.objects.get(pk=refferal_id)
                    referral.order = purchase
                    referral.purchase()
            response_data = {
                "StatusCode": 6000,
                "data": {"razorpay": order_data, "purchase": purchase.id},
            }
        else:
            response_data = {"StatusCode": 6001, "data": {"message": "No cart items"}}
    except Exception as e:
        transaction.rollback()
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["POST"])
def return_items(request, pk):
    try:
        if not PurchaseItems.objects.filter(pk=pk).exists():
            response_data = {
                "StatusCode": 6001,
                "data":{
                    "message":"purchase item not found"
                }
            }

        purchase_item = PurchaseItems.objects.get(pk=pk)
        purchase_item.is_returned = True
        purchase_item.save()

        return_data = Return.objects.create(
            purchase_item = purchase_item,
            reason = "Test"
        )
        return_log = ReturnStatusLog.objects.create(
            return_model = return_data,
            status = "pending"
        )
        response_data = {
            "StatusCode":6000,
            "data":{
                "message":"returned item successfully"
            }
        }
    except Exception as e:
        transaction.rollback()
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["POST"])
def cancel_items(request, pk):
    try:
        # Check if the purchase item exists
        if not PurchaseItems.objects.filter(pk=pk).exists():
            return Response({
                "StatusCode": 6001,
                "data": {
                    "message": "Order item not exists"
                }
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get the purchase item
        purchase_item = PurchaseItems.objects.get(pk=pk)
        
        # Check if the user is authorized to cancel this item
        if purchase_item.purchase.user != request.user:
            return Response({
                "StatusCode": 6001,
                "data": {
                    "message": "You are not authorized to cancel this item"
                }
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Mark the item as cancelled
        purchase_item.is_cancelled = True
        purchase_item.save()
        
        # Return success response
        return Response({
            "StatusCode": 6000,
            "data": {
                "message": "Item cancelled successfully"
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        # Rollback the transaction in case of error
        transaction.rollback()
        return Response({
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @api_view(["POST"])
# def purchase_items(request):
#     response_data = {}
#     try:
#         user = request.user
#         print(user)

#         try:
#             cart = Cart.objects.get(user=user)
#             print(cart)
#         except Cart.DoesNotExist:
#             response_data = {
#                 "status": 6001,
#                 "message": "Cart not found",
#             }
#             return Response({'app_data': response_data}, status=status.HTTP_200_OK)

#         total_amount = cart.total_amount
#         print(total_amount)
#         serializer = PurchaseAmountSerializer(data=request.data)
#         if serializer.is_valid():
#             user_serializer = UserSerializer(user)
#             serialized_user = user_serializer.data
#             print("Serialized User:", serialized_user)
#             payment_method = request.data["payment_method"]
#             tax_amount = int(request.data["tax_amount"])

#             # Check if the user wants to use the wallet
#             use_wallet = request.data.get("use_wallet", False)
#             wallet_deduction = 0

#             if use_wallet:
#                 # Check if the user has sufficient balance in the wallet
#                 wallet_balance = user.wallet.balance
#                 if wallet_balance > 0:
#                     # Deduct from the user's wallet up to its balance
#                     wallet_deduction = min(total_amount, wallet_balance)
#                     user.wallet.balance -= wallet_deduction
#                     user.wallet.save()

#                     # Adjust the total amount
#                     total_amount -= wallet_deduction

#             # Final amount is calculated
#             final_amount = total_amount + tax_amount
#             purchase_amount = PurchaseAmount.objects.create(
#                 user=user,
#                 total_amount=total_amount,
#                 tax=tax_amount,
#                 final_amount=final_amount,
#                 payment_method=payment_method,
#                 wallet_deduction=wallet_deduction,
#             )
#             purchase_log = PurchaseLog.objects.create(
#                 Purchases=purchase_amount
#             )
#             purchase = Purchase.objects.create(
#                 user=user,
#                 total_amount=total_amount
#             )

#             for cart_item in cart.cart_items.all():
#                 purchase_item = PurchaseItems.objects.create(
#                     purchase=purchase,
#                     product=cart_item.product,
#                     quantity=cart_item.quantity,
#                     price=cart_item.price,
#                 )
#                 try:
#                     attribute = Attribute.objects.get(product_varient__product=cart_item.product)
#                     attribute.quantity -= cart_item.quantity
#                     attribute.save()
#                 except Attribute.DoesNotExist:
#                     response_data = {
#                         "status": 6001,
#                         "message": "Attribute does not exist"
#                     }

#             # Clear the user's cart after the purchase
#             cart.cart_items.all().delete()
#             cart.delete()
#             response_data = {
#                 "status": 6000,
#                 "message": "Success",
#                 "data": {
#                     "user": user,  # This is likely the source of the error
#                     "total": total_amount,
#                     "tax_amount": tax_amount,
#                     "Final Amount": final_amount,
#                     "payment_method": payment_method,
#                     "use_wallet": use_wallet,
#                     "wallet_deduction": wallet_deduction,
#                 }
#             }
#         else:
#             response_data = {
#                 "status": 6001,
#                 "message": "Serializer validation failed",
#                 "errors": serializer.errors
#             }
#             return Response({'app_data': response_data}, status=status.HTTP_400_BAD_REQUEST)

#     except Exception as e:
#         response_data = {
#             "status": 6001,
#             "api": request.get_full_path(),
#             "request": request.data,
#             "message": str(e),
#         }

#     return Response({'app_data': response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
def viewPurchase(request):
    try:
        user = request.user
        purchase_items = PurchaseItems.objects.filter(purchase__user=user)

        if not purchase_items:
            response_data = {
                "StatusCode": 6001,
                "data": {"message": "Purchase Items Empty"},
            }
        if purchase_items:
            serializers = ViewPurchaseDeatils(purchase_items, many=True)
            response_data = {
                "StatusCode": 6000,
                "data": {"Purchased Item": serializers.data},
            }
            return Response({"app_data": response_data}, status=status.HTTP_200_OK)

    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
        return Response(
            {"app_data": response_data}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@permission_classes((AllowAny,))
def purchase_success(request, pk):
    try:
        purchase = Purchase.objects.get(pk=pk)
        purchase.active = True
        # Update purchase status and create a purchase log
        purchase.save()

        # Create an Invoice for the successful purchase
        invoice = Invoice.objects.create(
            issued_at=timezone.now(),
            customer_name=purchase.user.username,
            total_amount=purchase.total_amount,
            purchase=purchase,
            is_paid=True,
        )
        cart = Cart.objects.get(user=purchase.user)
        cart_items = CartItem.objects.filter(cart=cart)
        cart_items.delete()
        # Create a transaction log
        profile = UserProfile.objects.get(user=purchase.user)
        transaction_log = Transaction.objects.create(
            user=profile, amount=purchase.total_amount, success=True
        )
        purchase_logs = PurchaseLog.objects.create(
            purchase=purchase,
            status="Pending",
            description="Payment completed and preparing to for shipping",
        )
        # transaction = Transaction.objects.create()
        # transaction.commit()
        response_data = {
            "StatusCode": 6000,
            "data": {
                "invoice_id": invoice.id  # Include the created Invoice ID in the response if needed
            },
        }
        return Response({"app_data": response_data}, status=status.HTTP_200_OK)

    except Purchase.DoesNotExist:
        response_data = {"StatusCode": 6001, "data": {"message": "Purchase not found"}}
        return Response({"app_data": response_data}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@group_required(["admin"])
def view_oders(request):
    search = request.GET.get("q")
    filter = request.GET.get("filter")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    instances = Purchase.objects.filter(is_deleted=False).order_by("-created_at")  # Initialize instances here

    all_count = instances.count()
    Return_count = instances.filter(status="Return").count()
    shipped_count = instances.filter(status="Shipped").count()
    pending_orders = instances.filter(status="Pending").count()
    accepted_count = instances.filter(status="Accepted").count()
    delivered_count = instances.filter(status="Delivered").count()
    cancelled_count = instances.filter(status="Cancelled").count()
    
    
    if filter and filter != "All":
        instances = instances.filter(status=filter)

    if filter == "Return":
        instance = Return.objects.filter(is_deleted=False)
    if start_date and end_date:
        instances = instances.filter(created_at__range=[start_date, end_date]).order_by("-created_at")
    
    if search:
        instances = instances.filter(invoice_no__icontains=search)  
    
    paginator = Paginator(instances, 10)
    page = request.GET.get("page")

    try:
        instances = paginator.page(page)
    except PageNotAnInteger:
        instances = paginator.page(1)
    except EmptyPage:
        instances = paginator.page(paginator.num_pages)

    has_next_page = instances.has_next()
    next_page_number = instances.next_page_number() if has_next_page else 1

    has_previous_page = instances.has_previous()
    previous_page_number = instances.previous_page_number() if has_previous_page else 1

    if not filter == "Return":
        serializer = OrderSerializer(instances, many=True).data
    else:
        serializer = ReturnSerializer(instance, many=True).data


    response_data = {
        "StatusCode": 6000,
        "pending_orders": pending_orders,
        "all_count": all_count,
        "accepted_count": accepted_count,
        "shipped_count": shipped_count,
        "delivered_count": delivered_count,
        "cancelled_count": cancelled_count,
        "Return_count": Return_count,
        "data": serializer,
        "pagination_data": {
            "current_page": instances.number,
            "has_next_page": has_next_page,
            "next_page_number": next_page_number,
            "has_previous_page": has_previous_page,
            "previous_page_number": previous_page_number,
            "total_pages": paginator.num_pages,
            "total_items": paginator.count,
            "first_item": instances.start_index(),
            "last_item": instances.end_index(),
        },
    }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
def weekly_purchase(request):
    filter_by = request.GET.get("filter_by","this_month")
    
    labels = []
    data = []
    
    if filter_by == "last_week":
        daily_data = (
            Purchase.objects.annotate(day_start=TruncDay("created_at"))
            .values("day_start")
            .annotate(total_amount=Sum("total_amount"))
            .order_by("day_start")
        )

        labels = [day["day_start"].strftime("%Y-%m-%d") for day in daily_data]
        data = [day["total_amount"] for day in daily_data]
    elif filter_by == "this_month":
        weekly_data = (
            Purchase.objects.annotate(week_start=TruncWeek("created_at"))
            .values("week_start")
            .annotate(total_amount=Sum("total_amount"))
            .order_by("week_start")
        )

        labels = [week["week_start"].strftime("%Y-%m-%d") for week in weekly_data]
        data = [week["total_amount"] for week in weekly_data]
    elif filter_by == "this_year":
        monthly_data = (
            Purchase.objects.annotate(month_start=TruncMonth("created_at"))
            .values("month_start")
            .annotate(total_amount=Sum("total_amount"))
            .order_by("month_start")
        )

        labels = [month["month_start"].strftime("%Y-%m-%d") for month in monthly_data]
        data = [month["total_amount"] for month in monthly_data]

    response_data = {
        "StatusCode": 6000,
        "data": {
            "labels": labels,
            "data": data,
        },
    }

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
def order_stats(request):
    today = datetime.datetime.now().date()
    yesterday = today - timedelta(days=1)
    first_day_of_month = today.replace(day=1)
    last_day_of_last_month = first_day_of_month - timedelta(days=1)

    today_orders = Purchase.objects.filter(created_at__date=today)
    yesterday_orders = Purchase.objects.filter(created_at__date=yesterday)
    this_month_orders = Purchase.objects.filter(
        created_at__date__range=[first_day_of_month, today]
    )
    last_month_orders = Purchase.objects.filter(
        created_at__date__range=[last_day_of_last_month, first_day_of_month]
    )
    all_time_sales = Purchase.objects.all()

    stats = {
        "today_orders": today_orders.aggregate(total_amount=Sum("total_amount"))[
            "total_amount"
        ]
        or 0,
        "yesterday_orders": yesterday_orders.aggregate(
            total_amount=Sum("total_amount")
        )["total_amount"]
        or 0,
        "this_month_orders": this_month_orders.aggregate(
            total_amount=Sum("total_amount")
        )["total_amount"]
        or 0,
        "last_month_orders": last_month_orders.aggregate(
            total_amount=Sum("total_amount")
        )["total_amount"]
        or 0,
        "all_time_sales": all_time_sales.aggregate(total_amount=Sum("total_amount"))[
            "total_amount"
        ]
        or 0,
    }

    response_data = {
        "StatusCode": 6000,
        "data": stats,
    }

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
def product_count(request):
    out_of_stock = Product.objects.annotate(
                total_quantity=Sum("productattribute__quantity")
            ).filter(total_quantity=0).count()
    low_stock = Product.objects.annotate(
                total_quantity=Sum("productattribute__quantity")
            ).filter(total_quantity__gt=0, total_quantity__lte=20).count()
      

    stats = {
        "out_of_stock":out_of_stock ,
        "low_stock":low_stock ,
    }

    response_data = {
        "StatusCode": 6000,
        "data": stats,
    }

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)



@api_view(["GET"])
@group_required(
    [
        "admin",
    ]
)
def view_statusses(request):
    instance = PurchaseStatus.objects.all()
    serialized = PurchaseStatusSerializer(
        instance, context={"request": request}, many=True
    ).data
    response_data = {"StatusCode": 6000, "data": serialized}

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)
@api_view(["POST"])
def get_service_availability(request):
    try:
        pin_code = request.data["pin_code"]
    except:
        pin_code = None
    cart = Cart.objects.get(user=request.user)
    if not pin_code:
        response_data = {
            "StatusCode":6001,
            "data":{
                "message":"pin_code is required"
            }
        }
    if not cart:
        response_data = {
            "StatusCode":6001,
            "data":{
                "message":"Cart not found"
            }
        }
    try:
        service_availability = getServiceAvailability(cart, pin_code)
    except Exception as e:
        return Response({
            "StatusCode": 6002,
            "data": {
                "message": str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    response_data = {
        "StatusCode": 200,
        "data": service_availability
    }

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)

@api_view(["POST"])
@group_required(
    [
        "admin",
    ]
)
def add_purchase_log(request, pk):
    try:
        status_id = request.data["status"]
        description = request.data.get("description")

        purchase = get_object_or_404(Purchase, pk=pk)
        purchase_log = PurchaseLog.objects.create(
            Purchases=purchase, log_status=status_id, description=description
        )
        purchase.status = status_id
        purchase.save()
        create_order = None
        if status_id == "Accepted":
            # token = generateAccessShiprocket()
            create_order = createOrder(purchase)
        response_data = {
            "StatusCode": 6000,
            "data":{
                "message":"Successfully updated status",
                "response": create_order
            }
            }

    except Purchase.DoesNotExist:
        response_data = {"StatusCode": 6001, "data": {"message": "Purchase not found"}}
    except PurchaseStatus.DoesNotExist:
        response_data = {
            "StatusCode": 6001,
            "data": {"message": "PurchaseStatus not found with this id"},
        }
    except KeyError:
        response_data = {
            "StatusCode": 6001,
            "data": {"message": "status_id is required"},
        }

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@group_required(["admin"])
def view_order_count(request):
    try:
        purchase = Purchase.objects.filter(is_deleted=False)
        pending_purchase_count = purchase.filter(status="Pending").count()
        # pending_purchase_count = (
        #     PurchaseLogs.objects.filter(purchase__in=purchase, status__order_id=0)
        #     .distinct("purchase")
        #     .count()
        # )
        order_proccessing_count = (
            PurchaseLogs.objects.filter(purchase__in=purchase)
            .exclude(status__order_id__in=[0, 5])
            .distinct("purchase")
            .count()
        )
        completed_purchase_count = (
            PurchaseLogs.objects.filter(purchase__in=purchase, status__order_id=5)
            .distinct("purchase")
            .count()
        )
        total_count = purchase.count()

        response_data = {
            "StatusCode": 6000,
            "data": {
                "total_purchase_count": total_count,
                "completed_purchase_count": completed_purchase_count,
                "order_proccessing_count": order_proccessing_count,
                "pending_purchase_count": pending_purchase_count,
            },
        }
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
def create_refferal(request, pk):
    try:
        transaction.set_autocommit(False)
        try:
            refferal_code = request.data["refferal_code"]
        except:
            refferal_code = None

        try:
            email = request.data["email"]
        except:
            email = None
        if refferal_code:
            if UserProfile.objects.filter(refferal_code=refferal_code).exists():
                reffered_by = UserProfile.objects.get(refferal_code=refferal_code)
                if Product.objects.filter(pk=pk).exists():
                    product = Product.objects.get(pk=pk)
                    if email:
                        if UserProfile.objects.filter(email=email).exists():
                            reffered_to = UserProfile.objects.get(email=email)
                        else:
                            response_data = {
                                "StatusCode": 6001,
                                "data": {
                                    "message": "profile with this email not found"
                                },
                            }
                    else:
                        reffered_to = None

                    refferal = Referral.objects.create(
                        referred_by=reffered_by,
                        referred_to=reffered_to,
                        product=product,
                        refferal_status="pending",
                    )
                    transaction.commit()

                    response_data = {
                        "StatusCode": 6000,
                        "data": {"message": "success", "refferal_id": refferal.id},
                    }
                else:
                    response_data = {
                        "StatusCode": 6001,
                        "data": {"message": "Product not found"},
                    }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "data": {"message": "refferal_code not found"},
                }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {"message": "refferal_code is required"},
            }
    except Exception as e:
        transaction.rollback()
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
def update_all_refferal(request):
    try:
        refferals = Referral.objects.filter(refferal_status="completed")
        for refferal in refferals:
            product = refferal.product
            return_day = product.return_in
            purchase = refferal.order
            purchase_log = PurchaseLogs.objects.filter(purchase=purchase).latest(
                "created_at"
            )
            if purchase_log.status.order_id == 5:
                return_day = purchase_log.created_at + return_day
                if return_day == datetime.date.today():
                    refferal.refferal_status = "completed"
                    refferal.save()
                profile = UserProfile.objects.filter(user=refferal.referred_by)
                if Wallet.objects.filter(referred_by=profile).exists():
                    wallet = Wallet.objects.get(referred_by=profile)
                    amount = float(wallet.balance) + float(refferal.referral_amount)
                    wallet.balance = amount
                    wallet.save()
        response_data = {"StatusCode": 6000, "data": {"message": "success"}}
    except Exception as e:
        transaction.rollback()
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
# @group_required(["admin"])
@permission_classes((AllowAny,))
def admin_referals(request):
    try:
        instances = Referral.objects.all().order_by("-created_at")
        paginator = Paginator(instances, 10)
        page = request.GET.get("page")

        try:
            instances = paginator.page(page)
        except PageNotAnInteger:
            instances = paginator.page(1)
        except EmptyPage:
            instances = paginator.page(paginator.num_pages)

        has_next_page = instances.has_next()
        next_page_number = instances.next_page_number() if has_next_page else 1

        has_previous_page = instances.has_previous()
        previous_page_number = (
            instances.previous_page_number() if has_previous_page else 1
        )
        serialized = RefferalSerializer(
            instances, many=True, context={"request": request}
        ).data
        response_data = {
            "StatusCode": 6000,
            "data": serialized,
            "pagination_data": {
                "current_page": instances.number,
                "has_next_page": has_next_page,
                "next_page_number": next_page_number,
                "has_previous_page": has_previous_page,
                "previous_page_number": previous_page_number,
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "first_item": instances.start_index(),
                "last_item": instances.end_index(),
            },
        }
    except Exception as e:
        transaction.rollback()
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["view_refferal"])
@permission_classes((AllowAny,))
def view_refferal(request):
    try:
        response_data = {"StatusCode": 6000}
    except Exception as e:
        transaction.rollback()
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)

@api_view(["GET"])
def user_orders(request):
    try:
        response_data = {"StatusCode": 600}
    except Exception as e:
        transaction.rollback()
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)

@api_view(["POST"])
def admin_create_orders(request):
    try:
        serialized_data = OrderSerializer(data=request.data)
        if serialized_data.is_valid():
            invoice_number = 0
            # invoice_number = request.data["invoiceNumber"]
            customer_name = request.data["customerName"]
            address = request.data["deliveryAddress"]
            billing_address = request.data["billingAddress"]
            # post_code = request.data["post_code"]
            # street = request.data["street"]
            # city = request.data["city"]
            # state = request.data["state"]
            # country = request.data["country"]
            email = request.data["email"]
            phone = request.data["phone"]
            # password = request.data["password"]
            method = request.data["method"]
            source = request.data["source"]
            product_data = request.data.get('products', [])

            # if User.objects.filter(username=email).exists():
            #     response_data = {
            #         "StatusCode": 6001,
            #         "data": {"message": "Email already exists."}
            #     }
            #     return Response({"app_data": response_data}, status=status.HTTP_400_BAD_REQUEST)

            source_obj= Sources.objects.get(id=source)

            if email:
                # email = request.data["email"]
                # password = request.data["password"]
                profile = None
                user = None
                
                if User.objects.filter(username=email).exists():    
                    user = User.objects.get(username=email)
                    
                    if UserProfile.objects.filter(user=user).exists():
                        profile = UserProfile.objects.get(user=user)
                else:
                    user = User.objects.create_user(username=email, password=email)
                    
                if not profile:
                    enc_password = encrypt(email)

                    profile = UserProfile.objects.create(
                        user=user,
                        first_name=customer_name,
                        email=email,
                        password=enc_password,
                        phone_number = phone,
                        user_type = "manual",
                    )
            
                address = Address.objects.create(user=profile, 
                    first_name=customer_name,
                    address = address,
                    # post_code=post_code,
                    # street=street,
                    # city=city,
                    # state=state,
                    # country=country,
                    phone = phone,
                    )

            # total_amount = 0
            # for item in product_data:
            #   total_amount += int(item.get('totalPrice', 0) or 0)

            # if Invoice.objects.filter(invoice_no=invoice_number).exists():
            #     response_data = {
            #         "StatusCode": 6002,
            #         "data": {"message": "Invoice number already exists."}                  }
            #     return Response({"app_data": response_data}, status=status.HTTP_400_BAD_REQUEST)

            purchase = Purchase.objects.create(
                    user=user,
                    total_amount = 0,
                    invoice_no = invoice_number,
                    status = "Accepted",
                    address = address,
                    method =method,
                    source = source_obj,
                )
            
            PurchaseLog.objects.create(
                Purchases=purchase,
                log_status="Accepted"
            )
            

            for item_data in product_data:
                product = Product.objects.get(id=item_data.get('productName'))

                PurchaseItems.objects.create(
                    purchase=purchase,
                    product = product, 
                    price=product.price,
                    # attribute = item_data.get('product_attribute'),
                    quantity = item_data.get('quantity'),
                    # price = item_data.get('unitPrice'),                                  
                )
            total_amount = purchase.update_total_amount()
            current_time = datetime.datetime.now().date()
            invoice = Invoice.objects.create(
                    invoice_no = invoice_number,
                    issued_at = current_time,
                    customer_name = customer_name,
                    total_amount = total_amount,
                    purchase = purchase,
                )

            # create transaction object
            transaction = Transaction.objects.create(
                user=profile,
                amount=total_amount,
                success=True,
                credit=True,
                purchase=purchase,
                transaction_type=method,
            )            
           
            response_data = {
                "StatusCode": 6000,
                "data": {"message": "Order added successfully"},
            }
        else:
            response_data = {"StatusCode": 6001, "data": serialized_data.errors}

    except Exception as e:
        transaction.rollback()
        errType = e.__class__.__name__
        errors = {errType: traceback.format_exc()}
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
            "response": errors,
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
def order_source_list(request):
    try:
        if(sources:=Sources.objects.filter(is_deleted=False)).exists():
            serialized_data = SourcesSerializer(sources,many=True)
            response_data = {
                "StatusCode": 6000, 
                "data":serialized_data.data 
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "message": "Source not found"
                },
            }
    except Exception as e:
        transaction.rollback()
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@csrf_exempt
def download_invoice(request, pk):

    invoice_data = get_invoice_data(pk)
    logo_url = request.build_absolute_uri(static('/images/youngsta_logo.png'))

    if invoice_data is None:
        return HttpResponse('Order not found', status=404)

    html_string = render_to_string('activities/invoice/invoice.html', {'order': invoice_data,'logo_url':logo_url})
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=invoice_{invoice_data["order_details"]["invoice_number"]}.pdf'

    pdf = BytesIO()
    pisa_status = pisa.CreatePDF(html_string, dest=pdf)

    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
 
    response.write(pdf.getvalue())
    return response


@api_view(["GET"])
def wallet(request):
    try:
        user = request.user
        profile = UserProfile.objects.get(user=user)
        if Wallet.objects.filter(user=profile).exists():
            wallet = Wallet.objects.get(user=profile)
            response_data = {"StatusCode": 6000, "data": {"balance": wallet.balance}}
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {"message": "no wallet found for the user"},
            }
    except Exception as e:
        transaction.rollback()
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
def wallet_transaction(request):
    try:
        user = request.user
        profile = UserProfile.objects.filter(user=user)
        refferals = Referral.objects.filter(referred_by=user)
        response_data = {
            "StatusCode": 6000,
        }
    except Exception as e:
        transaction.rollback()
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
def orders(request):
    try:
        user = request.user
        instances = Purchase.objects.filter(active=True, user=user, is_deleted=False).order_by(
            "-created_at"
        )
        serializers = OrderSerializer(
            instances, many=True, context={"request": request}
        ).data
        response_data = {"StatusCode": 6000, "data": serializers}
    except Exception as e:
        transaction.rollback()
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)

@api_view(["GET"])
def orders_details(request,pk):
    try:
        user = request.user
        if Purchase.objects.filter(pk=pk).exists():
            purchase = Purchase.objects.get(pk=pk)
            instances = PurchaseItems.objects.filter(purchase=purchase)
            # serializers = OrderDetailSerializer(instances,many=True)
            serializers = PurchaseItemSerializer(instances,many=True)
            purchase_searializer = OrderSerializer(purchase,context={"request":request})

            response_data = {
                "StatusCode":6000,
                "data":{
                    "data":serializers.data,
                    "purchase_data":purchase_searializer.data,
                    "title":"Success",
                    "message":"Successfully fetched order details"
                }
            }
        else:
            response_data ={
                "StatusCode":6001,
                "data":{
                    "message":"order not found"
                }
            }
    except Exception as e:
        transaction.rollback()
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)

@api_view(["GET"])
def view_accounts(request):
    try:
        # Retrieve all transactions and order by id
        instances = Transaction.objects.filter(is_deleted=False).order_by("-id")

        # Pagination
        paginator = Paginator(instances, 10)  # Change 10 to your desired page size
        page_number = request.GET.get("page")
        instances = paginator.get_page(page_number)
        has_next_page = instances.has_next()
        has_previous_page = instances.has_previous()
        next_page_number = instances.next_page_number() if has_next_page else None
        previous_page_number = (
            instances.previous_page_number() if has_previous_page else None
        )

        # Serialize transactions data
        serialized = TransactionListSerializer(instances, many=True).data

        # Calculate credit and debit amounts
        credit = Transaction.objects.filter(is_deleted=False, credit=True).aggregate(
            Sum("amount")
        )["amount__sum"]
        debit = Transaction.objects.filter(is_deleted=False, credit=False).aggregate(
            Sum("amount")
        )["amount__sum"]

        # Prepare response data
        amounts_data = {"credit": credit, "debit": debit}
        pagination_data = {
            "current_page": instances.number,
            "has_next_page": has_next_page,
            "next_page_number": next_page_number,
            "has_previous_page": has_previous_page,
            "previous_page_number": previous_page_number,
            "total_pages": paginator.num_pages,
            "total_items": paginator.count,
            "first_item": instances.start_index(),
            "last_item": instances.end_index(),
        }
        response_data = {
            "StatusCode": 6000,
            "data": serialized,
            "amounts_data": amounts_data,
            "pagination_data": pagination_data,
        }
        return Response({"app_data": response_data}, status=status.HTTP_200_OK)
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
        return Response(
            {"app_data": response_data}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
def view_oder_detail(request, pk):
    if Purchase.objects.filter(pk=pk).exists():
        purchase = Purchase.objects.get(pk=pk)
        user_profile = UserProfile.objects.get(user=purchase.user)
        instance = PurchaseItems.objects.filter(purchase=purchase)
        serialized = PurchaseItemSerializer(instance, many=True).data
        address = AddressSerializer(purchase.address).data
        response_data = {
            "StatusCode": 6000,
            "data": {
                "name": f"{user_profile.first_name} {user_profile.last_name if user_profile.last_name else None}",
                "total_amount": purchase.total_amount,
                "status": purchase.status,
                "order_data": purchase.created_at,
                "products": serialized,
                "address": address,
                "shipment_id": purchase.SR_shipment_id,
                "order_id": purchase.SR_order_id,
            },
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "data": {"message": "Order with id not found"},
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
def purchase_failure(request, pk):
    try:
        purchase = Purchase.objects.get(pk=pk)
        purchase.delete()
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
def accounts_details(request):
    # try:
    instance = Transaction.objects.all().order_by("created_at")
    filter_value = request.GET.get("filter")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    if filter_value == "Credit":
        instance = instance.filter(credit=True)
    elif filter_value == "Debit":
        instance = instance.filter(credit=False)
    elif filter_value == "Withdrawal":
        # Assuming you meant to apply a different filter for "Withdrawal"
        instance = instance.filter(withdrawal=True)
    if start_date and end_date:
        instance = instance.filter(created_at__range=[start_date, end_date])
    paginator = Paginator(instance, 10)  # Change 10 to your desired page size
    page_number = request.GET.get("page")
    paginated_instance = paginator.get_page(page_number)
    has_next_page = paginated_instance.has_next()
    has_previous_page = paginated_instance.has_previous()
    next_page_number = (
        paginated_instance.next_page_number() if has_next_page else None
    )
    previous_page_number = (
        paginated_instance.previous_page_number() if has_previous_page else None
    )
    
    serialized = TransactionListSerializer(paginated_instance, many=True).data
    credited_amount = instance.filter(credit=True).aggregate(
        credited=Sum("amount")
    )["credited"]
    debited_amount = instance.filter(credit=False).aggregate(
        credited=Sum("amount")
    )["credited"]
    credited_amount = credited_amount if credited_amount is not None else 0
    debited_amount = debited_amount if debited_amount is not None else 0
    pagination_data = {
        "current_page": paginated_instance.number,
        "has_next_page": has_next_page,
        "next_page_number": next_page_number,
        "has_previous_page": has_previous_page,
        "previous_page_number": previous_page_number,
        "total_pages": paginator.num_pages,
        "total_items": paginator.count,
        "first_item": paginated_instance.start_index(),
        "last_item": paginated_instance.end_index(),
    }
    response_data = {
        "StatusCode": 6000,
        "data": {
            "credited": credited_amount,
            "debited": debited_amount,
            "transactions": serialized,
            "pagination_data": pagination_data,
        },
    }
    # except Exception as e:
    #     response_data = {
    #         "status": 0,
    #         "api": request.get_full_path(),
    #         "request": request.data,
    #         "message": str(e),
    #     }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_referral(request):
    try:
        referral_code = request.data.get("referral_code")
        if not referral_code:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "message": "Referral code is required"
                }
            }
            return Response({"app_data": response_data}, status=status.HTTP_200_OK)
        if not UserProfile.objects.filter(refferal_code=referral_code).exists():
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "message": "Referral code not valid"
                }
            }
            return Response({"app_data": response_data}, status=status.HTTP_200_OK)
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)
            for cart_item in cart_items:
                cart_item.referral_code = referral_code
                cart_item.save()
            response_data = {
                "StatusCode": 6000,
                "data": {
                    "message": "Referral code added successfully"
                }
            }
        except Cart.DoesNotExist:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "message": "Cart not found for the user"
                }
            }
        except Exception as e:
            response_data = {
                "StatusCode": 6002,
                "data": {
                    "message": f"An error occurred: {str(e)}"
                }
            }
        return Response({"app_data": response_data}, status=status.HTTP_200_OK)
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
        return Response({"app_data": response_data}, status=status.HTTP_200_OK)



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def apply_coupen(request):
    response_data = {}  # Initialize response_data at the beginning
    try:
        coupon_code = request.data.get("coupon_code")
        if not coupon_code:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "message": "Coupon code is required"
                }
            }
            return Response({"app_data": response_data}, status=status.HTTP_200_OK)
        
        coupen = Coupens.objects.filter(code=coupon_code).first()
        if not coupen:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "message": "Invalid coupon code"
                }
            }
            return Response({"app_data": response_data}, status=status.HTTP_200_OK)
        
        if coupen.is_expired:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "message": "Coupon code is expired"
                }
            }
            return Response({"app_data": response_data}, status=status.HTTP_200_OK)

        cart = Cart.objects.get(user=request.user)
        cart.total_amount = cart.total_amount or Decimal('0.00')  # Ensure total_amount is not None

        offer_start_price = coupen.offer_start_price or Decimal('0.00')
        offer_end_price = coupen.offer_end_price or Decimal('0.00')

        if coupen.offer and coupen.offer != 0:
            discount_amount = (cart.total_amount * coupen.offer) / 100
            if offer_start_price <= cart.total_amount <= offer_end_price:
                cart.total_amount -= discount_amount
                cart.coupon_code = coupon_code
                cart.coupen_offer = discount_amount
                cart.save()
                response_data = {
                    "StatusCode": 6000,
                    "data": {
                        "message": "Coupon applied successfully",
                        "discount_amount": discount_amount,
                        "total_amount": cart.total_amount
                    }
                }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "data": {
                        "message": "Coupon code is not applicable for this order"
                    }
                }

        elif coupen.offer_price and coupen.offer_price != 0:
            if offer_start_price <= cart.total_amount <= offer_end_price:
                cart.total_amount -= coupen.offer_price
                cart.coupen_offer = coupen.offer_price
                cart.coupon_code = coupon_code
                cart.save()
                response_data = {
                    "StatusCode": 6000,
                    "data": {
                        "message": "Coupon applied successfully",
                        "discount_amount": coupen.offer_price,
                        "total_amount": cart.total_amount
                    }
                }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "data": {
                        "message": "Coupon code is not applicable for this order"
                    }
                }

    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_financial_years(request):
    
    try:
        if FinancialYear.objects.filter(is_deleted=False).exists():
            financial_years = FinancialYear.objects.filter(is_deleted=False)
            
            serialized_data = FinancialYearsSerializer(financial_years,many=True).data
            
            response_data = {
                "StatusCode": 6000,
                "data": {
                    "data":serialized_data,
                    "title": "Success",
                    "message": "Successfully fetched financial years",
                }
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "title": "Failed",
                    "message":"Financial Years not found"
                }
            }
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_financial_year(request):
    
    try:
        serializer = CreateFinancialYearSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            response_data = {
                "StatusCode": 6000,
                "data": {
                    "message": "Successfully created financial year",
                }
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "message": "Invalid request",
                    "errors": serializer.errors
                }
            }
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_financial_year_status(request,pk):
    
    try:
        status_ = request.data.get("status","active")
        
        if FinancialYear.objects.filter(pk=pk,is_deleted=False).exists():
            financial_year = FinancialYear.objects.filter(pk=pk,is_deleted=False).first()
            
            financial_year.status = status_
            financial_year.save()
            
            response_data = {
                "StatusCode": 6000,
                "data": {
                    "message": "Status updated successfully",
                }
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "message": "Invalid request",
                    "errors": "Financial year not found"
                }
            }
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_financial_year_status(request,pk):
    
    try:
        
        if FinancialYear.objects.filter(pk=pk,is_deleted=False).exists():
            financial_year = FinancialYear.objects.filter(pk=pk,is_deleted=False).first()
            
            financial_year.delete()
            
            response_data = {
                "StatusCode": 6000,
                "data": {
                    "message": "Financial Year deleted successfully",
                }
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "message": "Invalid request",
                    "errors": "Financial year not found"
                }
            }
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


"""
    CREDIT NOTE
"""


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_credit_notes(request):
    
    try:
        if CreditNote.objects.filter(is_deleted=False).exists():
            credit_notes = CreditNote.objects.filter(is_deleted=False)
            
            serialized_data = CreditNotesSerializer(credit_notes,many=True).data
            
            response_data = {
                "StatusCode": 6000,
                "data": {
                    "data": serialized_data,
                    "title": "Success",
                    "message": "Successfully fetched credit notes",
                }
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "title": "Failed",
                    "message":"Credit Notes not found"
                }
            }
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
        
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_credit_note(request):
    
    try:
        serializer = CreateCreditNoteSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            response_data = {
                "StatusCode": 6000,
                "data": {
                    "message": "Successfully created credit note",
                }
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "message": "Invalid request",
                    "errors": serializer.errors
                }
            }
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
    
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)



@csrf_exempt
def download_credit_note(request, pk):
    
    if CreditNote.objects.filter(pk=pk,is_deleted=False).exists():
        credit_note = CreditNote.objects.filter(pk=pk,is_deleted=False).first()
        purchase_items = []
        total_amount = 0
        
        for purchase_item in credit_note.cancelled_items.filter(is_deleted=False):
            item_total = float(purchase_item.price if purchase_item.price else 0) * float(purchase_item.quantity if purchase_item.quantity else 1)
            
            purchase_items.append({
                "description": purchase_item.product.description,
                "product_code": purchase_item.product.product_code,
                "name": purchase_item.product.name,
                "quantity": purchase_item.quantity,
                "price": purchase_item.price,
                "total": item_total,
            })
            total_amount += item_total
    
        logo_url = request.build_absolute_uri(static('/images/youngsta_logo.png'))
        html_string = render_to_string('activities/credit-note/credit_note.html', {
            'credit_note': credit_note,
            "logo_url":logo_url,
            "purchase_items":purchase_items,
            "total_amount":total_amount,
        })
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={credit_note.credit_note_number}.pdf' 

        pdf = BytesIO()
        pisa_status = pisa.CreatePDF(html_string, dest=pdf)

        if pisa_status.err:
            return HttpResponse('Error generating PDF', status=500)
    
        response.write(pdf.getvalue())
        return response
    else:
        return HttpResponse('Credit not found', status=404)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def track_order_by_shipment_id(request,shipment_id):
    
    try:        
        if Purchase.objects.filter(SR_shipment_id=shipment_id,user=request.user).exists():
            response = getTrackingDetailsByShipmentID(shipment_id)
            response_data = {
                "StatusCode": 6000,
                "data": {
                    "data": response,
                }
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "title": "Invalid request",
                    "message": "Purchase Not Found",
                }
            }
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
    
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)