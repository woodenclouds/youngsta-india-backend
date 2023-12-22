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
