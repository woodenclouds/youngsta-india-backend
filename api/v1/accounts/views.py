import requests
import traceback

from django.db.models import Q
from django.db import transaction
from django.contrib.auth import logout
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from django.contrib.auth.models import Group, User
from django.contrib.auth import authenticate, login, logout

from .serializers import *
from api.v1.main.functions import *
from accounts.models import *
from payments.models import *
from main.encryptions import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
# from .functions import *
from api.v1.main.decorater import *
from .functions import *


@api_view(["POST"])
@permission_classes((AllowAny,))
def signup(request):
    try:
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            first_name = serializer.validated_data.get("first_name")
            last_name = serializer.validated_data.get("last_name")
            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password")

            if not UserProfile.objects.filter(email=email).exists():
                otp = ''.join([str(random.randint(0, 9)) for _ in range(4)])

                if not Otp.objects.filter(email=email).exists():
                    ot_obj = Otp.objects.create(email=email, otp=otp)
                    send_otp_email(email, otp)
                    user = User.objects.create_user(username=email, password=password)
                    enc_password = encrypt(password)
                    profile = UserProfile.objects.create(
                        user=user,
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        password=enc_password
                    )
                    # Assuming address data is nested within the UserProfileSerializer
                    # Retrieve and process address data
                    address_data = request.data.get("address", [])
                    if address_data:
                        for address_item in address_data:
                            Address.objects.create(user_profile=profile, **address_item)

                    transaction.commit()
                    response_data = {
                        "StatusCode": 6000,
                        "data": {"message": "Successfully sent otp's"}
                    }
                else:
                    response_data = {
                        "StatusCode": 6001,
                        "data": {"message": "OTP is expired, please resend"}
                    }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "data": {"message": "User with this email already exists"}
                }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": generate_serializer_errors(serializer._errors)
            }
    except Exception as e:
        transaction.rollback()
        errType = e.__class__.__name__
        errors = {errType: traceback.format_exc()}
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
            "response": errors
        }
    return Response({'app_data': response_data}, status=status.HTTP_200_OK)



@api_view(["POST"])
@permission_classes((AllowAny,))
def verify(request):
    try:
        transaction.set_autocommit(False)
        serializer = VerifySerializers(data=request.data)
        if serializer.is_valid():
            email = request.data["email"]
            otp = request.data["otp"]
            if Otp.objects.filter(email=email).exists():
                otp_obj = Otp.objects.filter(email=email).latest('created_at')
                if not otp_obj.is_expired():
                    if otp_obj.otp == otp:
                        otp_obj.delete()
                        profile = UserProfile.objects.get(email=email)
                        profile.is_verified = True
                        profile.save()
                        user = profile.user
                        refresh = RefreshToken.for_user(user)
                        access = str(refresh.access_token)
                        transaction.commit()
                        response_data = {
                            "StatusCode":6000,
                            "data":{
                                "first_name":profile.first_name,
                                "last_name":profile.last_name,
                                "email":profile.email,
                                "country_code":profile.country_code,
                                "phone_number":profile.phone_number,
                                "access_token": str(refresh.access_token),
                                "refresh_token": str(refresh)
                            }
                        }
                    else:
                        response_data={
                            "StatusCode":6001,
                            "data":{
                                "message":"incorrect otp"
                            }
                        }
                else:
                    otp_obj.delete()
                    response_data = {
                        "StatusCode":6001,
                        "data":{
                            "message":"OTP has been expired."
                        }
                    }
            else:
                response_data = {
                    "StatusCode":6001,
                    "data":{
                        "message":"no otp found with this email"
                    }
                }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": generate_serializer_errors(serializer._errors)
            }
    except Exception as e:
        transaction.rollback()
        errType = e.__class__.__name__
        errors = {
            errType: traceback.format_exc()
        }
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
            "response": errors
        }
    return Response({'app_data': response_data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    try:
        transaction.set_autocommit(False)
        serializer = LoginSerializers(data=request.data)
        if serializer.is_valid():
            email = request.data["email"]
            password = request.data["password"]
            user = authenticate(request, username=email, password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                access = str(refresh.access_token)
                profile = UserProfile.objects.get(user=user)
                if profile.is_verified:
                    response_data = {
                        "StatusCode": 6000,
                        "data": {
                            "first_name":profile.first_name,
                            "last_name":profile.last_name,
                            "email":profile.email,
                            "access_token": access,
                            "refresh_token": str(refresh)
                        }
                    }
                else:
                    response_data = {
                        "StatusCode":6001,
                        "data":{
                            "message":"email is not verified"
                        }
                    }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "data": {
                        "message": "Invalid credentials"
                    }
                }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": generate_serializer_errors(serializer._errors)
            }
    except Exception as e:
        transaction.rollback()
        errType = e.__class__.__name__
        errors = {
            errType: traceback.format_exc()
        }
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
            "response": errors
        }
    return Response({'app_data': response_data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
def admin_signup(request):
    try:
        transaction.set_autocommit(False)
        serializer = AdminSignupSerializers(data=request.data)
        if serializer.is_valid():
            name = request.data["name"]
            email = request.data["email"]
            password = request.data["password"]
            if not User.objects.filter(username=email).exists():
                user = User.objects.create_user(
                        username=email,
                        password=password
                )
                enc_password = encrypt(password)
                admin_profile = AdminProfile.objects.create(
                    user=user,
                    name = name,
                    email = email,
                    password = enc_password
                )
                transaction.commit()
                user = authenticate(request, username=email, password=password)
                add_user_to_group(email,'admin')
                refresh = RefreshToken.for_user(user)
                access = str(refresh.access_token)
                response_data = {
                    "StatusCode":6000,
                    "data":{
                        "message":"success",
                        "access":access,
                        "refresh":str(refresh)
                    }
                }
            else:
                response_data={
                    "StatusCode":6001,
                    "data":{
                        "message":"user exist with this email id"
                    }
                }
        else:
            response_data = {
                    "StatusCode": 6001,
                    "data": generate_serializer_errors(serializer._errors)
                }
    except Exception as e:
        transaction.rollback()
        errType = e.__class__.__name__
        errors = {
            errType: traceback.format_exc()
        }
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
            "response": errors
        }
    return Response({'app_data': response_data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
def admin_login(request):
    try:
        serializer = LoginSerializers(data=request.data)
        if serializer.is_valid():
            email = request.data["email"]
            password = request.data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None and user.is_active:
                print(user.username,"__________")
                refresh = RefreshToken.for_user(user)
                access = str(refresh.access_token)
                if AdminProfile.objects.filter(user=user).exists():
                    profile = AdminProfile.objects.get(user=user)
                    response_data = {
                        "StatusCode": 6000,
                        "data": {
                            # "first_name": profile.first_name,
                            # "last_name": profile.last_name,
                            "email": profile.email,
                            "access": access,
                            "refresh": str(refresh)
                        }
                    }
                else:
                    response_data = {
                        "StatusCode": 6001,
                        "data": {
                            "message": "user is not admin"
                        }
                    }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "data": {
                        "message": "incorrect password or user is inactive"
                    }
                }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": serializer.errors
            }
    except Exception as e:
        print("helloworld")
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
        return Response({'app_data': response_data}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({'app_data': response_data}, status=status.HTTP_200_OK)





# -------add adressses api-------



@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def add_address(request):
    try:
        user_profile = request.user.userprofile  # Get the user profile associated with the authenticated user
        addresses_count = Address.objects.filter(user=user_profile).count()

        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            address = serializer.save(user=user_profile)
            
            if addresses_count == 0:  # Set the first added address as primary
                address.primary = True
                address.save()

            response_data = {
                "StatusCode": 6000,
                "data": {
                    "message": "Address added successfully",
                    "address": serializer.data
                }
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": serializer.errors
            }

    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e)
        }

    return Response({'app_data': response_data}, status=status.HTTP_200_OK)




@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def view_addresses(request):
    try:
        user_profile = request.user.userprofile  # Get the user profile associated with the authenticated user
        addresses = Address.objects.filter(user=user_profile)
        serializer = AddressSerializer(addresses, many=True)

        response_data = {
            "StatusCode": 6000,
            "data": {
                "addresses": serializer.data
            }
        }

    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e)
        }

    return Response({'app_data': response_data}, status=status.HTTP_200_OK)


@api_view(["PUT"])
@permission_classes((IsAuthenticated,))
def change_primary_address(request, address_id):
    try:
        user_profile = request.user.userprofile  # Get the user profile associated with the authenticated user
        address = Address.objects.get(id=address_id, user=user_profile)
        other_addresses = Address.objects.filter(user=user_profile).exclude(id=address_id)

        if address:
            address.primary = True
            address.save()

            for other_addr in other_addresses:
                other_addr.primary = False
                other_addr.save()

            response_data = {
                "StatusCode": 6000,
                "data": {
                    "message": "Primary address changed successfully",
                    "address_id": address_id
                }
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "message": "Address not found"
                }
            }

    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e)
        }

    return Response({'app_data': response_data}, status=status.HTTP_200_OK)


@api_view(["PUT"])
@permission_classes((IsAuthenticated,))
def edit_address(request, address_id):
    try:
        user_profile = request.user.userprofile  # Get the user profile associated with the authenticated user
        address = Address.objects.get(id=address_id, user=user_profile)

        if address:
            serializer = AddressSerializer(address, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                response_data = {
                    "StatusCode": 6000,
                    "data": {
                        "message": "Address updated successfully",
                        "address": serializer.data
                    }
                }
            else:
                response_data = {
                    "StatusCode": 400,
                    "data": serializer.errors
                }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "message": "Address not found"
                }
            }

    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e)
        }

    return Response({'app_data': response_data}, status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes((IsAuthenticated,))
def delete_address(request, address_id):
    try:
        user_profile = request.user.userprofile  # Get the user profile associated with the authenticated user
        address = Address.objects.get(id=address_id, user=user_profile)

        if address:
            is_primary = address.primary
            address.delete()

            if is_primary:
                # If the deleted address was primary, update the primary status for another address
                new_primary_address = Address.objects.filter(user=user_profile).first()
                if new_primary_address:
                    new_primary_address.primary = True
                    new_primary_address.save()
                else:
                    user_profile.has_primary_address = False
                    user_profile.save()

            response_data = {
                "StatusCode": 6000,
                "data": {
                    "message": "Address deleted successfully",
                    "address_id": address_id
                }
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "message": "Address not found"
                }
            }

    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e)
        }

    return Response({'app_data': response_data}, status=status.HTTP_200_OK)
