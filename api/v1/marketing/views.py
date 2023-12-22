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
@group_required(["admin"])  # Replace with your permission logic
def add_advertisement(request):
    try:
        serializer = AdsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response_data = {
                "StatusCode": 600,
                "data": serializer.data,
                "message": "Advertisement added successfully"
            }
            return Response({'app_data': response_data}, status=status.HTTP_201_CREATED)
        else:
            response_data = {
                "StatusCode": 6001,
                "data": serializer.errors,
                "message": "Invalid data"
            }
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
    return Response({'app_data': response_data}, status=status.HTTP_400_BAD_REQUEST)




@api_view(["GET"])
@group_required(["admin"])
def view_advertisement(request):
    try:
        advertisements = Ads.objects.all()
        serialized = AdsSerializer(advertisements, many=True).data
        response_data = {
            "StatusCode": 6000,
            "data": serialized
        }
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
    return Response({'app_data': response_data}, status=status.HTTP_200_OK)



@api_view(["PUT", "PATCH"])
@group_required(["admin"])
def edit_ads(request, pk):
    try:
        advertisement = Ads.objects.get(pk=pk)
        serializer = AdsSerializer(advertisement, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            response_data = {
                "StatusCode": 6000,
                "data": serializer.data,
                "message": "Advertisement updated successfully"
            }
            return Response({'app_data': response_data}, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "data": serializer.errors,
                "message": "Invalid data"
            }
    except Ads.DoesNotExist:
        response_data = {
            "StatusCode": 404,
            "message": "Advertisement does not exist"
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
@group_required(["admin"])  # Add your permission logic here
def delete_ads(request, pk):
    try:
        ad = Ads.objects.get(pk=pk)
        ad.ad_items.all().delete()  # Delete related ad items
        ad.delete()  # Delete the ad
        response_data = {
            "StatusCode": 200,
            "message": f"Advertisement '{ad.title}' deleted successfully with its related items"
        }
    except Ads.DoesNotExist:
        response_data = {
            "StatusCode": 404,
            "message": "Advertisement does not exist"
        }
    except Exception as e:
        response_data = {
            "StatusCode": 500,
            "message": f"An error occurred: {str(e)}"
        }

    return Response({'app_data': response_data}, status=status.HTTP_200_OK)



@api_view(["POST"])
@group_required(["admin"])  # Replace with your permission logic
def add_aditem(request):
    try:
        serializer = AdsItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response_data = {
                "StatusCode": 600,
                "data": serializer.data,
                "message": "AdItem added successfully"
            }
            return Response({'app_data': response_data}, status=status.HTTP_201_CREATED)
        else:
            response_data = {
                "StatusCode": 601,
                "data": serializer.errors,
                "message": "Invalid data"
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
@group_required(["admin"])
def edit_aditem(request, pk):
    try:
        ad_item = AdsItem.objects.get(pk=pk)
        serializer = AdsItemSerializer(ad_item, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            response_data = {
                "StatusCode": 200,
                "data": serializer.data,
                "message": "AdItem updated successfully"
            }
            return Response({'app_data': response_data}, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 400,
                "data": serializer.errors,
                "message": "Invalid data"
            }
    except AdsItem.DoesNotExist:
        response_data = {
            "StatusCode": 404,
            "message": "AdItem does not exist"
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
@group_required(["admin"])
def delete_aditem(request, pk):
    try:
        ad_item = AdsItem.objects.get(pk=pk)
        ad_item.delete()
        response_data = {
            "StatusCode": 200,
            "message": "AdItem deleted successfully"
        }
    except AdsItem.DoesNotExist:
        response_data = {
            "StatusCode": 404,
            "message": "AdItem does not exist"
        }
    except Exception as e:
        response_data = {
            "StatusCode": 500,
            "message": f"An error occurred: {str(e)}"
        }

    return Response({'app_data': response_data}, status=status.HTTP_200_OK)