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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


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
                "message": "Advertisement added successfully",
            }
            return Response({"app_data": response_data}, status=status.HTTP_201_CREATED)
        else:
            response_data = {
                "StatusCode": 6001,
                "data": serializer.errors,
                "message": "Invalid data",
            }
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
    return Response({"app_data": response_data}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@group_required(["admin"])
def view_advertisement(request):
    try:
        advertisements = Ads.objects.all()
        serialized = AdsSerializer(advertisements, many=True).data
        response_data = {"StatusCode": 6000, "data": serialized}
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


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
                "message": "Advertisement updated successfully",
            }
            return Response({"app_data": response_data}, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "data": serializer.errors,
                "message": "Invalid data",
            }
    except Ads.DoesNotExist:
        response_data = {"StatusCode": 404, "message": "Advertisement does not exist"}
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
    return Response({"app_data": response_data}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@group_required(["admin"])  # Add your permission logic here
def delete_ads(request, pk):
    try:
        ad = Ads.objects.get(pk=pk)
        ad.ad_items.all().delete()  # Delete related ad items
        ad.delete()  # Delete the ad
        response_data = {
            "StatusCode": 200,
            "message": f"Advertisement '{ad.title}' deleted successfully with its related items",
        }
    except Ads.DoesNotExist:
        response_data = {"StatusCode": 404, "message": "Advertisement does not exist"}
    except Exception as e:
        response_data = {"StatusCode": 500, "message": f"An error occurred: {str(e)}"}

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


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
                "message": "AdItem added successfully",
            }
            return Response({"app_data": response_data}, status=status.HTTP_201_CREATED)
        else:
            response_data = {
                "StatusCode": 601,
                "data": serializer.errors,
                "message": "Invalid data",
            }
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
    return Response({"app_data": response_data}, status=status.HTTP_400_BAD_REQUEST)


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
                "message": "AdItem updated successfully",
            }
            return Response({"app_data": response_data}, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 400,
                "data": serializer.errors,
                "message": "Invalid data",
            }
    except AdsItem.DoesNotExist:
        response_data = {"StatusCode": 404, "message": "AdItem does not exist"}
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
    return Response({"app_data": response_data}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@group_required(["admin"])
def delete_aditem(request, pk):
    try:
        ad_item = AdsItem.objects.get(pk=pk)
        ad_item.delete()
        response_data = {"StatusCode": 200, "message": "AdItem deleted successfully"}
    except AdsItem.DoesNotExist:
        response_data = {"StatusCode": 404, "message": "AdItem does not exist"}
    except Exception as e:
        response_data = {"StatusCode": 500, "message": f"An error occurred: {str(e)}"}

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@group_required(["admin"])
def add_coupen(request):
    try:
        transaction.set_autocommit(False)
        serialized = AddCoupenSerializer(data=request.data)
        if serialized.is_valid():
            # Extract data from the validated serializer
            try:
                offer = serialized.validated_data["offer"]
            except:
                offer = None
            try:
                offer_start_price = request.data["offer_start_price"]
            except:
                offer_start_price = None
            try:
                offer_end_price = request.data["offer_end_price"]
            except:
                offer_end_price = None
            try:
                offer_price = request.data["offer_price"]
            except:
                offer_price = None
            description = serialized.validated_data["description"]
            validity = serialized.validated_data["validity"]

            # Create the Coupens object
            coupen = Coupens.objects.create(
                offer=offer,
                description=description,
                validity=validity,
                offer_start_price=offer_start_price,
                offer_end_price=offer_end_price,
                offer_price=offer_price,
            )

            transaction.commit()
            response_data = {
                "StatusCode": 6000,
                "data": {
                    "message": "Successfully added coupen",
                    "coupen_code": coupen.code,
                },
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": serialized.errors,
                "message": "Invalid data",
            }
    except Exception as e:
        response_data = {"StatusCode": 6001, "message": f"An error occurred: {str(e)}"}
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["POST"])
def editCoupen(request, pk):
    try:
        data = request.data
        if Coupens.objects.filter(pk=pk).exists():
            coupen = Coupens.objects.get(pk=pk)
            coupen.offer = data["offer"]
            coupen.offer_end_price = data["offer_end_price"]
            coupen.offer_start_price = data["offer_start_price"]
            coupen.offer_price = data["offer_price"]
            coupen.validity = data["validity"]
            coupen.save()
            response_data = {"StatusCode": 6000, "data": {"message": "coupen updated"}}
    except Exception as e:
        response_data = {"StatusCode": 6001, "message": f"An error occurred: {str(e)}"}
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["DELETE"])
def deleteCoupen(request, pk):
    try:
        if Coupens.objects.filter(pk=pk).exists():
            Coupens.objects.get(pk=pk).delete()
            response_data = {"StatusCode": 6000, "data": {"message": "deleted coupen"}}
    except Exception as e:
        response_data = {"StatusCode": 6001, "message": f"An error occurred: {str(e)}"}
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
def get_coupens(request):
    instances = Coupens.objects.all()
    paginator = Paginator(instances, 10)  # Show 10 instances per page.
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

    serialized = CoupenSerializer(
        instances, context={"request": request}, many=True
    ).data

    response_data = {
        "status": 6000,  # Changed StatusCode to status
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
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@group_required(["admin"])
def add_banner(request):
    try:
        banner_serializer = BannerSerializer(data=request.data)
        if banner_serializer.is_valid():
            section = request.data["section"]
            slider = request.data["slider"]
            items = request.data["items"]
            banner = Banners.objects.create(
                section=section,
                slider=slider
            )
            for item in items:
                banner_item = BannerItems.objects.create(
                    banner=banner,
                    image=item["image"],
                    order_id=item["order_id"],
                    filter=item["filter"]
                )
                
            response_data = {
                "StatusCode": 6000,
                "data": {
                    "message": "Successfully created"
                }
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "message": "Validation failed",
                    "errors": banner_serializer.errors
                }
            }
    except Exception as e:
        response_data = {"StatusCode": 6001, "message": f"An error occurred: {str(e)}"}
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@group_required(["admin"])
def view_banners(request):
    try:
        banners = Banners.objects.filter(is_deleted=False)
        serialized = BannerViewSerializer(
            banners, many=True
        ).data
        response_data = {
            "StatusCode":6000,
            "data":serialized
        }
    except Exception as e:
        response_data = {"StatusCode": 6001, "message": f"An error occurred: {str(e)}"}
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@group_required(["admin"])
def view_banner(request, pk):
    try:
        banner = Banners.objects.filter(pk=pk).first()
        if banner:
            banner_items = BannerItems.objects.filter(banner=banner)
            serialized = BannerListSerializer(banner_items, many=True).data
            
            response_data = {
                "StatusCode": 6000,
                "data": {
                    "slider": banner.slider,
                    "section": banner.section,
                    "items": serialized
                }
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "message": "Banner not found with this id"
                }
            }
    except Exception as e:
        response_data = {"StatusCode": 6001, "message": f"An error occurred: {str(e)}"}
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
def view_user_banner(request, section):
    try:
        banners = Banners.objects.filter(section=section)
        if banners.exists():
            banner_list = BannerItems.objects.filter(banner__in=banners)
            serialized = BannerListSerializer(banner_list, many=True).data
            response_data = {
                "StatusCode": 6000,
                "data": serialized
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "No banners found for this section"
            }
    except Exception as e:
        response_data = {"StatusCode": 6001, "message": f"An error occurred: {str(e)}"}
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@group_required(["admin"])
def update_banner(request, pk):
    try:
        banner_item = BannerItems.objects.filter(pk=pk).first()
        if banner_item:
            image = request.data.get("image", None)
            filter = request.data.get("filter", None)
            order_id = request.data.get("order_id", None)
            
            if image:
                banner_item.image = image
            if filter:
                banner_item.filter = filter
            if order_id:
                banner_item.order_id = order_id
                
            banner_item.save()
            response_data = {
                "StatusCode": 6000,
                "data": {
                    "message": "Banner updated successfully"
                }
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "message": "Banner item not found"
                }
            }
    except Exception as e:
        response_data = {"StatusCode": 6001, "message": f"An error occurred: {str(e)}"}
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
def enquiry(request):
    try:
        name = request.data.get("name", "")
        email = request.data.get("email", "")
        phone = request.data.get("phone", "")
        message = request.data.get("message", "")
        subject = request.data.get("subject", "")

        if not name or not email or not message:
            response_data = {
                "StatusCode": 6001,
                "message": "Name, phone number, and message are required fields"
            }
        else:
            enquiry = Enquiry.objects.create(
                name=name,
                email=email,
                phone=phone,
                message=message,
                subject=subject
            )

            response_data = {
                "StatusCode": 6000,
                "data": {
                    "message": "Enquiry submitted successfully",
                    "enquiry_id": enquiry.id
                }
            }
    except Exception as e:
        response_data = {"StatusCode": 6001, "message": f"An error occurred: {str(e)}"}
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@group_required(["admin"])
def admin_enquiry(request):
    try:
        instances = Enquiry.objects.all().order_by('-created_at')
        serialized = EnquirySerializer(
            instances,
            many=True
        ).data
        response_data = {
            "StatusCode":6000,
            "data": serialized
        }
    except Exception as e:
        response_data = {"StatusCode": 6001, "message": f"An error occurred: {str(e)}"}
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)

