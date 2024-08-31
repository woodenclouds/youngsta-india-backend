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
from activities.models import *


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
            phone = serializer.validated_data.get("phone_number")

            if not UserProfile.objects.filter(email=email).exists():
                otp = "".join([str(random.randint(0, 9)) for _ in range(4)])
                if len(phone) != 10:
                    response_data = {
                        "StatusCode": 6001,
                        "data": {"message": "Phone number must be 10 digits"},
                    }
                    
                if not Otp.objects.filter(email=email).exists():
                    ot_obj = Otp.objects.create(email=email, otp=otp)
                    send_otp_email(email, otp)
                    if User.objects.filter(email=email).exists():
                        user = User.objects.get(email=email)
                        if UserProfile.objects.filter(user=user, is_verified = False).exists():
                            profile = UserProfile.objects.get(user=user,is_verified = False)
                            profile.delete()
                            user.delete()
                        elif UserProfile.objects.filter(user=user, is_verified = True).exists():
                            response_data = {
                                "StatusCode": 6001,
                                "data": {"message": "User already exists"},
                                }
                            
                    user = User.objects.create_user(username=email, password=password)
                    enc_password = encrypt(password)
                    code = generate_referral_code()
                    profile = UserProfile.objects.create(
                        user=user,
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        password=enc_password,
                        refferal_code=code,
                        phone_number = phone
                    )
                    cart = Cart.objects.create(user=user)
                    wallet = Wallet.objects.create(
                        user=profile,
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
                        "data": {"message": "Successfully sent otp's"},
                    }
                else:
                    response_data = {
                        "StatusCode": 6001,
                        "data": {"message": "OTP is expired, please resend"},
                    }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "data": {"message": "User with this email already exists"},
                }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": generate_serializer_errors(serializer._errors),
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
            "response": errors,
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


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
                otp_obj = Otp.objects.filter(email=email).latest("created_at")
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
                            "StatusCode": 6000,
                            "data": {
                                "first_name": profile.first_name,
                                "last_name": profile.last_name,
                                "email": profile.email,
                                "country_code": profile.country_code,
                                "refferal_code": profile.refferal_code,
                                "phone_number": profile.phone_number,
                                "access_token": str(refresh.access_token),
                                "refresh_token": str(refresh),
                            },
                        }
                    else:
                        response_data = {
                            "StatusCode": 6001,
                            "data": {"message": "incorrect otp"},
                        }
                else:
                    otp_obj.delete()
                    response_data = {
                        "StatusCode": 6001,
                        "data": {"message": "OTP has been expired."},
                    }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "data": {"message": "no otp found with this email"},
                }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": generate_serializer_errors(serializer._errors),
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
            "response": errors,
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


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
                            "first_name": profile.first_name,
                            "last_name": profile.last_name,
                            "refferal_code": profile.refferal_code,
                            "email": profile.email,
                            "access_token": access,
                            "refresh_token": str(refresh),
                        },
                    }
                else:
                    response_data = {
                        "StatusCode": 6001,
                        "data": {"message": "email is not verified"},
                    }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "data": {"message": "Invalid credentials"},
                }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": generate_serializer_errors(serializer._errors),
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
            "response": errors,
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


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
                user = User.objects.create_user(username=email, password=password)
                enc_password = encrypt(password)
                admin_profile = AdminProfile.objects.create(
                    user=user,
                    name=name,
                    email=email,
                    password=enc_password,
                )
                transaction.commit()
                user = authenticate(request, username=email, password=password)
                add_user_to_group(email, "admin")
                refresh = RefreshToken.for_user(user)
                access = str(refresh.access_token)
                response_data = {
                    "StatusCode": 6000,
                    "data": {
                        "message": "success",
                        "access": access,
                        "refresh": str(refresh),
                    },
                }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "data": {"message": "user exist with this email id"},
                }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": generate_serializer_errors(serializer._errors),
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
            "response": errors,
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
def adminSignup(request):
    try:
        transaction.set_autocommit(False)
        serializer = AdminSignupSerializers(data=request.data)
        if serializer.is_valid():
            name = request.data["name"]
            email = request.data["email"]
            password = request.data["password"]
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=name,  # You can also set other user attributes here
                )
                encrypt_pass = encrypt(password)
                admin_profile = AdminProfile.objects.create(
                    user=user,
                    name=name,
                    password=encrypt_pass,
                    email=email,
                    country_code="US",
                    phone_number=00000000000,
                )
                add_user_to_group(email, "admin")
                transaction.commit()
                refresh = RefreshToken.for_user(user)
                access = str(refresh.access_token)
                response_data = {
                    "StatusCode": 6000,
                    "data": {
                        "message": "success",
                        "access": access,
                        "refresh": str(refresh),
                    },
                }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "data": {"message": "user already exists"},
                }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": generate_serializer_errors(serializer._errors),
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
            "response": errors,
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
def admin_login(request):
    try:
        serializer = LoginSerializers(data=request.data)
        if serializer.is_valid():
            email = request.data["email"]
            password = request.data["password"]
            user = authenticate(request, username=email, password=password)
            if user is not None and user.is_active:
                print(user.username, "__________")
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
                            "refresh": str(refresh),
                        },
                    }
                else:
                    response_data = {
                        "StatusCode": 6001,
                        "data": {"message": "user is not admin"},
                    }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "data": {"message": "incorrect password or user is inactive"},
                }
        else:
            response_data = {"StatusCode": 6001, "data": serializer.errors}
    except Exception as e:
        print("helloworld")
        response_data = {
            "StatusCode": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
        return Response(
            {"app_data": response_data}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@group_required(["admin"])
def costemers(request):
    try:
        search = request.GET.get("search")
        instances = UserProfile.objects.all()
        if search:
            instances = instances.filter(
                Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(email__icontains=search) | Q(phone_number__icontains = search)
            )
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

        serialized = ViewCostomerSerializer(
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
        print("helloworld")
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
        return Response(
            {"app_data": response_data}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


# -------add adressses api-------


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def add_address(request):
    try:
        user_profile = (
            request.user.userprofile
        )  # Get the user profile associated with the authenticated user
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
                    "address": serializer.data,
                },
            }
        else:
            response_data = {"StatusCode": 6001, "data": serializer.errors}

    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)

@api_view(["POST"])
def edit_account_details(request):
    try:
        first_name = request.data["first_name"]
        last_name = request.data["last_name"]
        mail = request.data["email"]
        phone_number = request.data["phone_number"]
        user = request.user
        if not UserProfile.objects.filter(user=user).exists():
            response_data = {
                "StatusCode":6001,
                "data":{
                    "message":"user not found"
                }
            }
        account_details = UserProfile.objects.get(user=user)
        account_details.first_name = first_name
        account_details.last_name = last_name
        account_details.email = mail
        account_details.phone_number = phone_number
        account_details.save()

        response_data ={ 
            "StatusCode":6000,
            "data":{
                "message":"Account details updated successfully"
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
def account_details(request):
    try:
        user = request.user
        if not UserProfile.objects.filter(user=user).exists():
            response_data = {
                "StatusCode":6001,
                "data":{
                    "message":"user not found"
                    }
                    }
        account_details = UserProfile.objects.get(user=user)
        response_data = {
            "StatusCode":6000,
            "data":{
                "first_name":account_details.first_name,
                "last_name":account_details.last_name,
                "email":account_details.email,
                "phone_number":account_details.phone_number,
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
@permission_classes((IsAuthenticated,))
def view_addresses(request):
    try:
        user_profile = (
            request.user.userprofile
        )  # Get the user profile associated with the authenticated user
        addresses = Address.objects.filter(user=user_profile)
        serializer = AddressSerializer(addresses, many=True)

        response_data = {"StatusCode": 6000, "data": {"addresses": serializer.data}}

    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["PUT"])
@permission_classes((IsAuthenticated,))
def change_primary_address(request, address_id):
    try:
        user_profile = (
            request.user.userprofile
        )  # Get the user profile associated with the authenticated user
        address = Address.objects.get(id=address_id, user=user_profile)
        other_addresses = Address.objects.filter(user=user_profile).exclude(
            id=address_id
        )

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
                    "address_id": address_id,
                },
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {"message": "Address not found"},
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
@permission_classes((IsAuthenticated,))
def edit_address(request, address_id):
    try:
        user_profile = (
            request.user.userprofile
        )  # Get the user profile associated with the authenticated user
        address = Address.objects.get(id=address_id, user=user_profile)

        if address:
            serializer = AddressSerializer(address, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                response_data = {
                    "StatusCode": 6000,
                    "data": {
                        "message": "Address updated successfully",
                        "address": serializer.data,
                    },
                }
            else:
                response_data = {"StatusCode": 6001, "data": serializer.errors}
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {"message": "Address not found"},
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
@permission_classes((IsAuthenticated,))
def delete_address(request, address_id):
    try:
        user_profile = (
            request.user.userprofile
        )  # Get the user profile associated with the authenticated user
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
                    "address_id": address_id,
                },
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {"message": "Address not found"},
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
@group_required(["admin"])
def addStaff(request):
    try:
        user = request.user
        transaction.set_autocommit(False)
        serialized_data = AddStaffSerializer(data=request.data)

        if serialized_data.is_valid():
            fullname = request.data["fullname"]
            email = request.data["email"]
            password = request.data["password"]
            type = request.data["type"]
            password = request.data["password"]
            enc_password = encrypt(password)

            # Create Staff instance
            staff = Staff.objects.create(
                user=user,
                fullname=fullname,
                email=email,
                password=enc_password,
                type=type,
            )
            # Serialize the created staff data
            staff_data = AddStaffSerializer(staff).data

            response_data = {
                "StatusCode": 6000,
                "data": {"message": "Staff added successfully", "staff": staff_data},
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
    finally:
        transaction.commit()

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["PUT", "PATCH"])
@group_required(["admin"])
def edit_staff(request, pk):
    try:
        staff = Staff.objects.get(pk=pk)
        if staff:
            serializer = StaffSerializer(staff, data=request.data, partial=True)
            print(serializer)
            if serializer.is_valid():
                # Use the serializer's update method to selectively update fields
                serializer.update(staff, serializer.validated_data)

                response_data = {
                    "StatusCode": 6000,
                    "data": {
                        "message": "Staff details updated successfully",
                        "data": serializer.data,
                    },
                }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "data": serializer.errors,  # Include serializer errors in the response
                }
        else:
            response_data = {"StatusCode": 6001, "data": {"message": "Staff not found"}}

    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
def viewstaff(request):
    try:
        instances = Staff.objects.all()
        serialized_instances = []

        for instance in instances:
            if instance.is_deleted == False:
                serialized_instances.append(StaffSerializer(instance).data)

        response_data = {"StatusCode": 6000, "data": serialized_instances}
    except Exception as e:
        transaction.rollback()
        errType = e._class.name_
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
@group_required(["admin"])
def delete_staff(request, pk):
    try:
        if Staff.objects.filter(pk=pk).exists():
            staff_detail = Staff.objects.get(pk=pk)
            staff_detail.delete()
            response_data = {
                "StatusCode": 6000,
                "message": "Staff deleted successfully",
            }
        else:
            response_data = {"StatusCode": 6001, "data": {"message": "staff not found"}}
    except Staff.DoesNotExist:
        response_data = {"StatusCode": 6001, "message": "Staff does not exist"}
    except Exception as e:
        response_data = {"StatusCode": 6001, "message": f"An error occurred: {str(e)}"}

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
def view_user(request):
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    response_data = {
        "StatusCode": 6000,
        "data": {
            "first_name": user_profile.first_name,
            "last_name": user_profile.last_name,
            "email": user_profile.email,
            "phone_number": user_profile.phone_number,
            "country_code": user_profile.country_code,
        },
    }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@group_required(["admin"])
def accountDetails(request):
    try:
        admin_account = AdminProfile.objects.get(user=request.user)
        response_data = {
            "StatusCode": 6000,
            "data": {"name": admin_account.name, "email": admin_account.email},
        }
    except Exception as e:
        response_data = {"StatusCode": 6001, "message": f"An error occurred: {str(e)}"}
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@group_required(["admin"])
def edit_account(request):
    try:
        try:
            name = request.data["name"]
        except:
            name = None
        if name:
            admin_account = AdminProfile.objects.get(user=request.user)
            admin_account.name = name
            admin_account.save()
        response_data = {
            "StatusCode": 6000,
            "data": {
                "message": "succesfully changed  your information",
            },
        }
    except Exception as e:
        response_data = {"StatusCode": 6001, "message": f"An error occurred: {str(e)}"}
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@group_required(["admin"])
def change_password(request):
    try:
        admin_account = AdminProfile.objects.get(user=request.user)
        try:
            old_pass = request.data["old_password"]
        except:
            old_pass = None
        try:
            new_pass = request.data["new_password"]
        except:
            new_pass = None
        if old_pass and new_pass:
            if admin_account.user.check_password(old_pass):
                admin_account.user.set_password(new_pass)
                enc_pass = encrypt(new_pass)
                admin_account.password = enc_pass
                admin_account.save()
                response_data = {
                    "StatusCode": 6000,
                    "data": {"message": "Succesfully changed password"},
                }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "Old password is incorrect",
                }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {"message": "old_pass and new_pass is required"},
            }
    except Exception as e:
        response_data = {"StatusCode": 6001, "message": f"An error occurred: {str(e)}"}
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["POST"])
def change_password(request):
    try:
        user = request.user
        user_profile = UserProfile.objects.get(user=user)
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        if not (old_password and new_password):
            response_data = {
                "StatusCode": 6001,
                "data": {"message": "old_password and new_password required"},
            }
            return Response(
                {"app_data": response_data}, status=status.HTTP_400_BAD_REQUEST
            )

        user_auth = authenticate(username=user_profile.email, password=old_password)
        if user_auth is None:
            response_data = {
                "StatusCode": 6001,
                "data": {"message": "Incorrect old password"},
            }
            return Response(
                {"app_data": response_data}, status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()
        encrypt_pass = encrypt(new_password)
        user_profile.password = encrypt_pass
        user_profile.save()

        response_data = {
            "StatusCode": 6000,
            "data": {"message": "Password changed successfully"},
        }
        return Response({"app_data": response_data}, status=status.HTTP_200_OK)

    except UserProfile.DoesNotExist:
        response_data = {
            "StatusCode": 6003,
            "data": {"message": "User profile not found"},
        }
        return Response({"app_data": response_data}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        response_data = {
            "StatusCode": 6004,
            "data": {"message": f"An error occurred: {str(e)}"},
        }
        return Response(
            {"app_data": response_data}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
