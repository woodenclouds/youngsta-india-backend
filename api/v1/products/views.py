from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.db.models import F, Value, IntegerField
from django.db import transaction
import traceback
from .serializers import *
from api.v1.main.decorater import *
from api.v1.main.functions import *
from products.models import *
from django.db.models import Case, When, Value, IntegerField
from rest_framework import generics
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime, timedelta
from django.db.models import Q
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.db.models.query import QuerySet


@api_view(["GET"])
@group_required(["admin"])
def admin_product(request):
    try:
        search = request.GET.get("search", "")
        category_id = request.GET.get("category", "")

        query = Product.objects.filter(
            Q(name__icontains=search) | Q(sub_category__name__icontains=search)
        )

        if category_id != "":
            category = Category.objects.get(pk=category_id)
            sub_categories = SubCategory.objects.filter(category=category)
            sub_category_ids = sub_categories.values_list("id", flat=True)
            inner_sub_categories = SubCategory.objects.filter(
                parent__in=sub_category_ids
            )
            inner_sub_category_ids = inner_sub_categories.values_list("id", flat=True)
            query = query.filter(
                Q(sub_category__in=sub_category_ids)
                | Q(sub_category__in=inner_sub_category_ids)
            )

        query = query.order_by("name")
        paginator = Paginator(query, 10)
        page = request.GET.get("page")

        try:
            products_page = paginator.page(page)
        except PageNotAnInteger:
            products_page = paginator.page(1)
        except EmptyPage:
            products_page = paginator.page(paginator.num_pages)

        has_next_page = products_page.has_next()
        next_page_number = products_page.next_page_number() if has_next_page else 1

        has_previous_page = products_page.has_previous()
        previous_page_number = (
            products_page.previous_page_number() if has_previous_page else 1
        )

        serialized = ProductAdminViewSerializer(products_page, many=True).data

        response_data = {
            "StatusCode": 6000,
            "data": serialized,
            "pagination_data": {
                "current_page": products_page.number,
                "has_next_page": has_next_page,
                "next_page_number": next_page_number,
                "has_previous_page": has_previous_page,
                "previous_page_number": previous_page_number,
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "first_item": products_page.start_index(),
                "last_item": products_page.end_index(),
            },
        }
    except (Product.DoesNotExist, Category.DoesNotExist, SubCategory.DoesNotExist):
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": "Product, Category, or SubCategory not found",
            "response": {},
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


from django.db.models import Max


@api_view(["POST"])
@group_required(["admin"])
def addCategory(request):
    try:
        transaction.set_autocommit(False)
        serializer = AddCategorySerializers(data=request.data)
        if serializer.is_valid():
            name = request.data["name"]
            description = request.data["description"]
            image = request.data["image"]
            cat_id = createsix()

            # Get the highest existing order
            highest_order = Category.objects.aggregate(Max("position"))["position__max"]

            # Set the order for the new category to be the next sequential number
            order = highest_order + 1 if highest_order is not None else 1

            category = Category.objects.create(
                name=name,
                description=description,
                image=image,
                cat_id=cat_id,
                position=order,
            )
            transaction.commit()
            print(cat_id)
            response_data = {
                "StatusCode": 6000,
                "data": {"message": "category created successfully"},
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


@api_view(["GET"])
@permission_classes((AllowAny,))
def categories(request):
    try:
        instances = Category.objects.order_by("position")
        serialized_instances = []

        page = request.GET.get("page", 1)
        paginator = Paginator(instances, 10)  # Show 10 instances per page.
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
        for instance in instances:
            if instance.is_deleted == False:
                serialized_instances.append(ViewCategorySerializer(instance).data)

        response_data = {
            "StatusCode": 6000,
            "data": serialized_instances,
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
@group_required(["admin"])
def adminCategories(request):
    try:
        page = request.GET.get("page", 1)
        instances = Category.objects.all().order_by("position")
        paginator = Paginator(instances, 10)
        try:
            paginated_instances = paginator.page(page)
        except PageNotAnInteger:
            paginated_instances = paginator.page(1)
        except EmptyPage:
            paginated_instances = paginator.page(paginator.num_pages)
        serialized = ViewCategorySerializer(paginated_instances, many=True)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data,
            "pagination_data": {
                "current_page": paginated_instances.number,
                "has_next_page": paginated_instances.has_next(),
                "next_page_number": paginated_instances.next_page_number() if paginated_instances.has_next() else None,
                "has_previous_page": paginated_instances.has_previous(),
                "previous_page_number": paginated_instances.previous_page_number() if paginated_instances.has_previous() else None,
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "first_item": paginated_instances.start_index(),
                "last_item": paginated_instances.end_index(),
            },
        }
    except Exception as e:
        transaction.rollback()
        errType = e.__class__.__name__
        errors = {errType: traceback.format_exc()}
        response_data = {
            "StatusCode": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
            "response": errors,
        }
    
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)
@api_view(["PUT", "PATCH"])
@group_required(["admin"])
def editCategory(request, pk):
    try:
        category = Category.objects.get(id=pk)
        serializer = EditCategorySerializer(category, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            response_data = {
                "StatusCode": 6000,
                "data": serializer.data,
                "message": "Category updated successfully",
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": generate_serializer_errors(serializer.errors),
            }
    except Category.DoesNotExist:
        response_data = {"StatusCode": 6002, "data": {"message": "Category not found"}}
    except Exception as e:
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


@api_view(["PUT", "PATCH"])
@permission_classes((AllowAny,))
def editCategoryPosition(request, pk):
    try:
        category = Category.objects.get(id=pk)
        serializer = EditCategoryPositionSerializer(
            instance=category, data=request.data
        )

        if serializer.is_valid():
            new_position = serializer.validated_data.get("position")

            # Check if the new position is within the valid range
            total_categories = Category.objects.count()
            if 1 <= new_position <= total_categories:
                with transaction.atomic():
                    current_position = category.position

                    # Shift categories below the target position up
                    if current_position < new_position:
                        Category.objects.filter(
                            position__gt=current_position, position__lte=new_position
                        ).update(position=models.F("position") - 1)
                    # Shift categories above the target position down
                    elif current_position > new_position:
                        Category.objects.filter(
                            position__lt=current_position, position__gte=new_position
                        ).update(position=models.F("position") + 1)

                    # Update the position of the current category
                    category.position = new_position
                    category.save()

                    response_data = {
                        "StatusCode": 6000,
                        "data": {
                            "message": f"Category position updated successfully to {new_position}"
                        },
                    }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "data": {"message": "Invalid position value"},
                }
        else:
            response_data = {
                "StatusCode": 6002,
                "data": generate_serializer_errors(serializer.errors),
            }
    except Category.DoesNotExist:
        response_data = {"StatusCode": 6003, "data": {"message": "Category not found"}}
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
            "response": {
                "error": "An error occurred while updating the category position"
            },
        }

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["DELETE"])
@group_required(["admin"])
def deleteCategory(request, pk):
    try:
        category = Category.objects.get(pk=pk)
        category_name = category.name
        category.delete()
        response_data = {
            "StatusCode": 6000,
            "data": {"message": f"{category_name} deleted successfully"},
        }
        return Response({"app_data": response_data}, status=status.HTTP_200_OK)
    except Category.DoesNotExist:
        response_data = {
            "StatusCode": 6001,
            "data": {"message": "Category not found"},
        }
        return Response({"app_data": response_data}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        errType = e.__class__.__name__
        errors = {errType: traceback.format_exc()}
        response_data = {
            "StatusCode": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
            "response": {"error": "An error occurred while deleting the category", "trace": errors},
        }
        return Response({"app_data": response_data}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@group_required(["admin"])
def addProduct(request):
    try:
        transaction.set_autocommit(False)
        serialized = AddProductSerializer(data=request.data)
        if serialized.is_valid():
            name = request.data["name"]
            description = request.data["description"]
            subcategoryId = request.data["subcategory_id"]
            price = request.data["price"]
            offers = request.data["offers"]
            purchase_price = request.data["purchase_price"]
            # brandId = request.data["brand_id"]
            error = False
            if not SubCategory.objects.filter(pk=subcategoryId).exists():
                error = True
                response_data = {
                    "StatusCode": 6001,
                    "data": {"message": "sub category not exist"},
                }
            # if not Brand.objects.filter(pk=brandId).exists():
            #     error = True
            #     response_data = {
            #         "StatusCode":6001,
            #         "data":{
            #             "message":"brand not exist"
            #         }
            #     }
            if Product.objects.filter(name=name).exists():
                error = True
                response_data = {
                    "StatusCode": 6001,
                    "data": {
                        "message": "product already exists",
                    },
                }
            if not error:
                subcategory = SubCategory.objects.get(pk=subcategoryId)
                # brand = Brand.objects.get(pk=brandId)
                product = Product.objects.create(
                    name=name,
                    description=description,
                    subcategory=subcategory,
                    price=price,
                    offers=offers,
                    purchase_price=purchase_price,
                )
                transaction.commit()
                response_data = {
                    "StatusCode": 6000,
                    "data": {
                        "message": f"{product.name} created succesfully",
                        "product": {
                            "id": product.id,
                            "name": product.name,
                        },
                    },
                }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": generate_serializer_errors(serialized._errors),
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
@group_required(["admin"])
def addVarient(request, pk):
    try:
        transaction.set_autocommit(False)
        error = False
        message = ""
        datas = request.data
        if not Product.objects.filter(pk=pk).exists():
            error = True
            message = "Product dous not exist"
        if not error:
            product = Product.objects.get(pk=pk)
            for data in datas:
                images = data.get("images")
                attributes = data.get("attributes")
                print(attributes, "_____atri___obj")
                product_varient = ProductVarient.objects.create(
                    product=product, thumbnail=images[0]
                )
                for image in images:
                    print(image, "______image")
                    product_image = ProductImages.objects.create(
                        image=image, product_varient=product_varient
                    )

                for attribute in attributes:
                    print(attribute, "test______test")
                    attribute_obj = Attribute.objects.create(
                        attribute=attribute["attribute"],
                        attribute_value=attribute["attribute_value"],
                        quantity=attribute["quantity"],
                    )
            transaction.commit()
            response_data = {
                "StatusCode": 6000,
                "data": {"message": "Succesfully created varient"},
            }
        else:
            response_data = {"StatusCode": 6001, "data": {"message": message}}
    except Exception as e:
        transaction.rollback()
        errType = e.__class__.__name__
        errors = {errType: traceback.format_exc()}
        response_data = {
            "status": 6001,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
            "response": errors,
        }

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@group_required(["admin"])
def addProductVarient(request, pk):
    try:
        transaction.set_autocommit(False)
        varients = request.data["varients"]
        attributes = request.data["attributes"]

        if Product.objects.filter(pk=pk).exists():
            product = Product.objects.get(pk=pk)
            product_varient = ProductVarient.objects.create(product=product)

            for varient in varients:
                image_url = varient.get("url")
                if image_url:
                    product_image, _ = ProductImages.objects.get_or_create(
                        image=varient.get("url"),
                        product_varient=product_varient,
                        primary=varient.get("thumbnail"),
                    )

            for attribute in attributes:
                print(attribute.get("attribute"), "______________hello world")
                attribute_id = attribute.get("attribute")
                if Attribute.objects.filter(pk=attribute_id).exists():
                    print(attribute.get("attribute"), "____id")
                    quantity = attribute.get("quantity")
                    attribute_model = Attribute.objects.get(pk=attribute_id)
                    print(attribute_model.attribute, "_____________helloooooo")
                    product_attribute = VarientAttribute.objects.create(
                        varient=product_varient,
                        attribute=attribute_model,
                        quantity=quantity,
                    )
            transaction.commit()
            response_data = {
                "StatusCode": 6000,
                "data": {
                    "message": "Success added varient",
                },
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {"message": "product not found"},
            }
    except Exception as e:
        transaction.rollback()
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
            "response": traceback.format_exc(),
        }

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@group_required(["admin"])
def addBrand(request):
    try:
        transaction.set_autocommit(False)
        serialized = AddBrandSerializer(data=request.data)
        if serialized.is_valid():
            name = request.data["name"]
            description = request.data["description"]
            image = request.data["image"]
            if Brand.objects.filter(name=name).exists():
                response_data = {
                    "StatusCode": 6001,
                    "data": "brand with this name already exists",
                }
            else:
                brand = Brand.objects.create(
                    name=name, description=description, image=image
                )
                transaction.commit()
                response_data = {
                    "StatusCode": 6000,
                    "data": {"message": f"{brand.name} created succesfully"},
                }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": generate_serializer_errors(serialized._errors),
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


# @api_view(["GET"])
# @permission_classes((AllowAny,))
# def brands(request):
#     try:
#         instance = Brand.objects.all()
#         serialized = BrandSerializer(
#             instance,
#             many=True
#         ).data
#         response_data = {
#             "StatusCode":6000,
#             "data":serialized
#         }
#     except Exception as e:
#         transaction.rollback()
#         errType = e.__class__.__name__
#         errors = {
#             errType: traceback.format_exc()
#         }
#         response_data = {
#             "status": 0,
#             "api": request.get_full_path(),
#             "request": request.data,
#             "message": str(e),
#             "response": errors
#         }
#     return Response({'app_data': response_data}, status=status.HTTP_200_OK)


# ---------view brand----------------
@api_view(["GET"])
@permission_classes((AllowAny,))
def brands(request):
    try:
        instances = Category.objects.all()
        serialized_instances = []

        for instance in instances:
            if instance.is_deleted == False:
                serialized_instances.append(BrandSerializer(instance).data)

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


@api_view(["PUT", "PATCH"])
@group_required(["admin"])
def editBrand(request, pk):
    try:
        # Get the existing category instance
        brand = Brand.objects.get(id=pk)
        # Deserialize the request data
        serializer = EditBrandSerializer(brand, data=request.data, partial=True)

        if serializer.is_valid():
            name = request.data.get("name")
            description = request.data.get("description")
            image = request.data.get("image")
            brand.name = name
            brand.description = description
            brand.image = image
            serializer.save()
            response_data = {
                "StatusCode": 6000,
                "data": serializer.data,
                "message": "brand updated successfully",
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": generate_serializer_errors(serializer.errors),
            }
    except Category.DoesNotExist:
        response_data = {"StatusCode": 6002, "data": {"message": " not found"}}
    except Exception as e:
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


# -----------------Delete brand ----------------------


@api_view(["DELETE"])
@group_required(["admin"])
def deleteBrand(request, pk):
    try:
        brand = Brand.objects.get(pk=pk)
        brand.is_deleted = True
        brand.save()
        response_data = {
            "StatusCode": 6000,
            "data": {"message": f"{brand.name} deleted Successfully"},
        }
    except Brand.DoesNotExist:
        response_data = {"StatusCode": 6001, "data": {"message": "Category not found"}}
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
            "response": {"error": "An error occurred while deleting the category"},
        }

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


# ----------views for adding atributes-------------


@api_view(["POST"])
@group_required(["admin"])
def addAttribute(request):
    try:
        serializer = AddAttributeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response_data = {
                "StatusCode": 6000,
                "data": {
                    "message": "Attribute added successfully",
                    "attribute": serializer.data,
                },
            }
            return Response({"app_data": response_data}, status=status.HTTP_201_CREATED)
        else:
            response_data = {"StatusCode": 6001, "data": serializer.errors}
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
    return Response({"app_data": response_data}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def listAttributes(request):
    try:
        instances = Attribute.objects.all()
        serialized_instances = []

        for instance in instances:
            if not instance.is_deleted:  # Check if 'is_deleted' is False
                serialized_instances.append(AttributeSerializer(instance).data)

        response_data = {"StatusCode": 6000, "data": serialized_instances}
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

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["PUT", "PATCH"])
@group_required(["admin"])
def editAttribute(request, pk):
    try:
        attribute = Attribute.objects.get(pk=pk)
        serializer = EditAttributeSerializer(attribute, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            response_data = {
                "StatusCode": 200,
                "data": serializer.data,
                "message": "Attribute updated successfully",
            }
            return Response({"app_data": response_data}, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 400,
                "data": serializer.errors,
                "message": "Invalid data",
            }
            return Response(
                {"app_data": response_data}, status=status.HTTP_400_BAD_REQUEST
            )

    except Attribute.DoesNotExist:
        response_data = {"StatusCode": 404, "message": "Attribute does not exist"}
        return Response({"app_data": response_data}, status=status.HTTP_404_NOT_FOUND)

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


@api_view(["DELETE"])
@group_required(["admin"])
def deleteAttribute(request, pk):
    try:
        if AttributeType.objects.filter(pk=pk).exists():
            attribute = AttributeType.objects.get(pk=pk)
            attribute.delete()  # Remove the attribute completely from the database
            response_data = {
                "StatusCode": 6000,
                "data": {
                    "message": f"Attribute '{attribute.name}' deleted successfully"
                },
            }
        else:
            response_data = {
                "StatusCode":6001,
                "data":{
                    "message":"attribute not found"
                }
            }
    except Attribute.DoesNotExist:
        response_data = {"StatusCode": 6001, "data": {"message": "Attribute not found"}}
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
            "response": {"error": "An error occurred while deleting the attribute"},
        }

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


# -----------------Sub Category ----------------------------------------------------------------


@api_view(["POST"])
@group_required(["admin"])
def addSubcategory(request, data=None):
    try:
        transaction.set_autocommit(False)
        serialized = AddSubCategorySerializer(data=request.data)
        category_id = request.data["category"]
        try:
            parent_id = request.data["parent_id"]
        except:
            parent_id = None

        errors = []

        if not serialized.is_valid():
            errors.append(generate_serializer_errors(serialized._errors))

        if not Category.objects.filter(pk=category_id).exists():
            errors.append("Category does not exist.")

        parent = None  # Default value for parent

        if parent_id and not SubCategory.objects.filter(pk=parent_id).exists():
            errors.append("Parent SubCategory does not exist.")
        elif parent_id:
            parent = SubCategory.objects.get(pk=parent_id)

        if "image" not in request.data :
            errors.append("Image is required.")
            
        if errors:
            response_data = {"StatusCode": 6001, "data": {"message": ", ".join(errors)}}
        else:
            name = request.data["name"]
            description = request.data["description"]
            image = request.data["image"]
            category = Category.objects.get(pk=category_id)

            highest_position = SubCategory.objects.aggregate(Max("position"))[
                "position__max"
            ]
            if parent_id:
                parent = SubCategory.objects.get(pk=parent_id)
            else:
                parent = None

            # Get the highest existing position for SubCategory under the same parent
            highest_position = SubCategory.objects.filter(parent=parent).aggregate(
                Max("position")
            )["position__max"]

            # Set the position for the new SubCategory to be the next sequential number
            position = highest_position + 1 if highest_position is not None else 1

            if not SubCategory.objects.filter(
                name=name, category=category, parent=parent
            ).exists():
                sub_category = SubCategory.objects.create(
                    name=name,
                    description=description,
                    image=image,
                    category=category,
                    parent=parent,
                    position=position,
                )

                transaction.commit()
                response_data = {
                    "StatusCode": 6000,
                    "data": {"message": f"{sub_category.name} successfully created"},
                }

                # Recursive call to handle adding multiple levels of subcategories
                if "subcategories" in request.data:
                    for subcategory_data in request.data["subcategories"]:
                        subcategory_data["category"] = category_id
                        subcategory_data["parent"] = sub_category.id
                        addSubcategory(request=request, data=subcategory_data)
            else:
                response_data = {
                    "StatusCode": 6001,
                    "data": {"message": "Subcategory already exists"},
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


@api_view(["GET"])
@permission_classes((AllowAny,))
def viewSubCategory(request, pk):
    try:
        print("hi")
        if Category.objects.filter(pk=pk).exists():
            parent_id = request.GET.get(
                "parent_id"
            )  # Get the parent_id from query params
            if parent_id:
                instances = SubCategory.objects.filter(category=pk, parent=parent_id)
            else:
                instances = SubCategory.objects.filter(category=pk, order=0)

            serialized_instances = [
                ViewSubCategorySerializer(instance).data for instance in instances
            ]

            response_data = {"StatusCode": 6000, "data": serialized_instances}
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {"message": "Category does not exist"},
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


@api_view(["GET"])
@group_required(
    [
        "admin",
    ]
)
def view_admin_single_product(request, pk):
    if Product.objects.filter(pk=pk).exists():
        instance = Product.objects.get(pk=pk)
        serialized = ProductAdminViewSerializer(
            instance, context={"request": request}
        ).data
        response_data = {"StatusCode": 6000, "data": serialized}
    else:
        response_data = {"StatusCode": 6001, "data": {"message": "product not found"}}
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


# def viewSubCategory(request, type):
#     try:
#         response_data = {}

#         if type == "all":
#             print(type,'___________________________________________')
#             instances = SubCategory.objects.filter(is_deleted=False)
#             serialized_instances = [ViewSubCategorySerializer(instance).data for instance in instances]
#             response_data = {
#                 "StatusCode": 6000,
#                 "data": {
#                     "message": serialized_instances
#                 }
#             }
#         elif SubCategory.objects.filter(pk=type, is_deleted=False).exists():
#             instances = SubCategory.objects.filter(pk=type, is_deleted=False)
#             serialized_instances = [ViewSubCategorySerializer(instance).data for instance in instances]
#             response_data["sub_category_exists"] = {
#                 "StatusCode": 6000,
#                 "data": {
#                     "message": serialized_instances
#                 }
#             }
#         elif SubCategory.objects.filter(category=type, is_deleted=False).exists():
#             instances = SubCategory.objects.filter(category=type, is_deleted=False)
#             serialized_instances = [ViewSubCategorySerializer(instance).data for instance in instances]
#             response_data["sub_category_belongs_to_category"] = {
#                 "StatusCode": 6000,
#                 "data": {
#                     "message": serialized_instances
#                 }
#             }
#         else:
#             response_data["invalid_condition"] = {
#                 "StatusCode": 6001,
#                 "data": {
#                     "message": "Invalid condition or Sub Category does not exist"
#                 }
#             }

#     except Exception as e:
#         errType = e.__class__.__name__
#         errors = {
#             errType: traceback.format_exc()
#         }
#         response_data = {
#             "status": 0,
#             "api": request.get_full_path(),
#             "request": request.data,
#             "message": str(e),
#             "response": errors
#         }

#     return Response({'app_data': response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
def get_category_tree(request):
    try:
        response_data = {"StatusCode": 6000}
    except Exception as e:
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


@api_view(["PUT", "PATCH"])
@group_required(["admin"])
def editSubCategory(request, pk):
    try:
        subcategory = SubCategory.objects.get(id=pk)
        serializer = EditSubCategorySerializer(
            subcategory, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()

            response_data = {
                "StatusCode": 6000,
                "data": serializer.data,
                "message": "Subcategory updated successfully",
            }

        # Handle validation errors
        else:
            response_data = {"StatusCode": 6001, "data": serializer.errors}

    except SubCategory.DoesNotExist:
        response_data = {
            "StatusCode": 6002,
            "data": {"message": "Subcategory not found"},
        }
    except Exception as e:
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


@api_view(["DELETE"])
@group_required(["admin"])
def deleteSubCategory(request, pk):
    try:
        if SubCategory.objects.filter(pk=pk).exists():
            category = SubCategory.objects.get(pk=pk)
            category.delete()
            response_data = {
                "StatusCode": 6000,
                "data": {"message": "removed sub category"},
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {"message": "sub category not found"},
            }

    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
            "response": {"error": "An error occurred while deleting the category"},
        }

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["PUT", "PATCH"])
@permission_classes((AllowAny,))
def editSubCategoryPosition(request, pk):
    try:
        category = SubCategory.objects.get(id=pk)
        serializer = EditSubCategoryPositionSerializer(
            instance=category, data=request.data
        )

        if serializer.is_valid():
            new_position = serializer.validated_data.get("position")

            # Check if the new position is within the valid range
            total_categories = SubCategory.objects.count()
            if 1 <= new_position <= total_categories:
                with transaction.atomic():
                    current_position = category.position

                    # Shift categories below the target position up
                    if current_position < new_position:
                        SubCategory.objects.filter(
                            position__gt=current_position, position__lte=new_position
                        ).update(position=models.F("position") - 1)
                    # Shift categories above the target position down
                    elif current_position > new_position:
                        SubCategory.objects.filter(
                            position__lt=current_position, position__gte=new_position
                        ).update(position=models.F("position") + 1)

                    # Update the position of the current category
                    category.position = new_position
                    category.save()

                    response_data = {
                        "StatusCode": 6000,
                        "data": {
                            "message": f"Category position updated successfully to {new_position}"
                        },
                    }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "data": {"message": "Invalid position value"},
                }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": generate_serializer_errors(serializer.errors),
            }
    except SubCategory.DoesNotExist:
        response_data = {"StatusCode": 6001, "data": {"message": "Category not found"}}
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
            "response": {
                "error": "An error occurred while updating the category position"
            },
        }

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


# -----------------Sub Category End----------------------------------------------------------------

# =========== Product =================================================================


@api_view(["POST"])
@group_required(["admin"])
def addProductItem(request, pk):
    try:
        transaction.set_autocommit(False)
        serialized = AddProductItemSerializer(data=request.data)
        error = False
        if not serialized.is_valid():
            error = True
            response_data = {
                "StatusCode": 6001,
                "data": generate_serializer_errors(serialized._errors),
            }
        if not Product.objects.filter(pk=pk).exists():
            response_data = {
                "StatusCode": 6001,
                "data": {"message": "product with this pk not exist"},
            }
        if not error:
            product = Product.objects.get(pk=pk)
            color = request.data["color"]
            stock = request.data["stock"]
            size = request.data["size"]
            images = request.data.get("images", [])
            print(images, "_________imag")
            product_item = ProductItem.objects.create(
                color=color, stock=stock, size=size, product=product
            )
            # for image in images:
            #     print(image,"_______image_______")
            # product_image = ProductImages.objects.create(
            #     product_item = product_item,
            #     image = image
            # )
            transaction.commit()
            response_data = {
                "StatusCode": 6000,
                "data": {"message": "created product item"},
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


# ----------------------- Products -----------------------------------------
# @api_view(["GET"])
# @permission_classes((AllowAny,))
# def viewProduct(request):
#     try:
#         response_data = {}

#         def get_product_instances(query, search_query=None):
#             base_query = Q(**query, is_deleted=False)

#             if search_query:
#                 search_query = search_query.strip()
#                 search_condition = (
#                     Q(category__name__icontains=search_query) |
#                     Q(category__description__icontains=search_query) |
#                     Q(subcategory__name__icontains=search_query) |
#                     Q(subcategory__description__icontains=search_query) |
#                     Q(name__icontains=search_query) |
#                     Q(description__icontains=search_query)
#                 )
#                 instances = Product.objects.filter(base_query & search_condition)
#                 serialized = ProductViewSerializer(instances, context={"request": request}, many=True).data
#             else:
#                 instances = Product.objects.filter(base_query)
#                 serialized = ProductViewSerializer(instances, context={"request": request}, many=True).data
#             return serialized

#         type = request.GET.get('type', 'all')  # Set default value to 'all' if not provided
#         type_conditions = {
#             "all": {},
#             "numeric": lambda t: {'id': t.isdigit()},
#             # Add more conditions as needed
#         }

#         query = type_conditions.get(type, None)
#         search_query = request.GET.get('search', None)

#         if query is None:
#             response_data = {
#                 "StatusCode": 6001,
#                 "data": {
#                     "message": "Invalid type or Product not found or deleted"
#                 }
#             }
#             return Response({'app_data': response_data}, status=status.HTTP_200_OK)

#         response_data = {
#             "StatusCode": 6000,
#             "data": get_product_instances(query, search_query=search_query)
#         }

#     except Exception as e:
#         transaction.rollback()
#         errType = e.__class__.__name__
#         errors = {
#             errType: traceback.format_exc()
#         }
#         response_data.update({
#             "status": 6001,
#             "api": request.get_full_path(),
#             "request": request.data,
#             "message": str(e),
#             "response": errors
#         })

#     return Response({'app_data': response_data}, status=status.HTTP_200_OK)


def get_sub_categories(sub_categories):
    products = []
    for sub_category in sub_categories:
        if SubCategory.objects.filter(parent=sub_category).exists():
            sub_categories_under_sub = SubCategory.objects.filter(parent=sub_category)
            products.extend(get_sub_categories(sub_categories_under_sub))
        products.extend(Product.objects.filter(sub_category=sub_category))
    return products


# from django.db.models import Q

def get_products_by_category_name(category_name):
    # Fetch the category
    category = Category.objects.filter(name=category_name).first()
    if not category:
        return Product.objects.none()  # No products if category doesn't exist

    # Fetch all related subcategories (including nested ones)
    def get_all_subcategories(subcategories):
        children = SubCategory.objects.filter(parent__in=subcategories)
        if children.exists():
            return subcategories | get_all_subcategories(children)
        return subcategories

    top_level_subcategories = SubCategory.objects.filter(category=category)
    all_subcategories = get_all_subcategories(top_level_subcategories)

    # Filter products by subcategories
    products = Product.objects.filter(sub_category__in=all_subcategories)
    return products



@api_view(["GET"])
@permission_classes((AllowAny,))
def viewProduct(request):
    try:
        search_query = request.GET.get("search", "")
        tags = request.GET.get("tags", "")
        category_name = request.GET.get("category", "")
        price_range = request.GET.get("price", "")

        query = Product.objects.all()

        if search_query:
            query = query.filter(
                Q(name__icontains=search_query)
                | Q(sub_category__name__icontains=search_query)
            )

        if tags == "featured-products":
            query = query.filter(featured=True)
        elif tags == "new-arrival-products":
            query = query.annotate(num_purchases=Count("purchaseitems"))
        elif tags == "on-selling-products":
            query = query.annotate(num_purchases=Count("purchaseitems"))
        elif tags == "flash-sale-products":
            query = query.filter(flash_sale=True)
        
        if price_range:
            price_range = price_range.split("-")
            min_price = float(price_range[0])
            max_price = float(price_range[1] if price_range[1] else 1000000)
            query = query.filter(price__gte=min_price, price__lte=max_price)
            
        # if category_name:
        #     category = Category.objects.get(name=category_name)
        #     sub_categories = SubCategory.objects.filter(category=category)
        #     sub_category_ids = sub_categories.values_list("id", flat=True)
        #     inner_sub_categories = SubCategory.objects.filter(
        #         parent__in=sub_category_ids
        #     )
        #     inner_sub_category_ids = inner_sub_categories.values_list("id", flat=True)
        #     query = query.filter(
        #         Q(sub_category__in=sub_category_ids)
        #         | Q(sub_category__in=inner_sub_category_ids)
        #     )
            
        if category_name:
            category_name = category_name.replace("-", " ")
            query = get_products_by_category_name(category_name)
            # try:
            #     category = Category.objects.get(Q(name__icontains=category_name))
            #     print(category,"categoryyyyy")
            #     subcategories = SubCategory.objects.filter(category=category).values_list("id",flat=True)
            #     if query.filter(sub_category__in=subcategories).exists():
            #         query = query.filter(sub_category__in=subcategories)
            #     else:
            #         query = get_sub_categories(subcategories)
            # except Category.DoesNotExist:
            #     subcategory = SubCategory.objects.filter(name__icontains=category_name).first()
            #     if subcategory:
            #         if query.filter(sub_category=subcategory).exists():
            #             query = query.filter(sub_category=subcategory)
            #         else:
            #             query = get_sub_categories([subcategory])
                # else:
                #     query = Product.objects.none()
        
        if isinstance(query, QuerySet):
            query = query.order_by("name")
        else:
            query.sort(key=lambda x: x.name)

        # if all(isinstance(item, Product) for item in query):
        #     query = query.distinct()

        query = list(set(query))

        paginator = Paginator(query, 10)
        page = request.GET.get("page")

        try:
            products_page = paginator.page(page)
        except PageNotAnInteger:
            products_page = paginator.page(1)
        except EmptyPage:
            products_page = paginator.page(paginator.num_pages)

        has_next_page = products_page.has_next()
        next_page_number = products_page.next_page_number() if has_next_page else 1

        has_previous_page = products_page.has_previous()
        previous_page_number = (
            products_page.previous_page_number() if has_previous_page else 1
        )

        serialized = ProductViewSerializer(
            products_page, many=True, context={"request": request}
        ).data

        response_data = {
            "StatusCode": 6000,
            "data": serialized,
            "pagination_data": {
                "current_page": products_page.number,
                "has_next_page": has_next_page,
                "next_page_number": next_page_number,
                "has_previous_page": has_previous_page,
                "previous_page_number": previous_page_number,
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "first_item": products_page.start_index(),
                "last_item": products_page.end_index(),
            },
        }
        return Response({"app_data": response_data}, status=status.HTTP_200_OK)

    except (Product.DoesNotExist, Category.DoesNotExist, SubCategory.DoesNotExist) as e:
        return Response(
            {
                "status": 0,
                "api": request.get_full_path(),
                "request": request.data,
                "message": "Product, Category, or SubCategory not found",
                "response": {},
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    except Exception as e:
        traceback.print_exc()
        return Response(
            {
                "status": 6001,
                "api": request.get_full_path(),
                "request": request.data,
                "message": str(e),
                "response": traceback.format_exc(),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes((AllowAny,))
def viewProductSingle(request, pk):
    try:
        if Product.objects.filter(pk=pk).exists():
            product = Product.objects.get(pk=pk)
            serialized = ProductViewSerializer(
                product, context={"request": request}
            ).data
            response_data = {"StatusCode": 6000, "data": serialized}
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {"message": "Product dous not exist with this pk"},
            }
    except Exception as e:
        transaction.rollback()
        errType = e.__class__.__name__
        errors = {errType: traceback.format_exc()}
        response_data = {
            "status": 6001,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
            "response": errors,
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
def subcategory_tree(request, pk):
    print("hai djksjdmskmd")
    if Category.objects.filter(pk=pk).exists():
        category = Category.objects.get(pk=pk)
        categories = SubCategory.objects.filter(parent__isnull=True, category=category)

        def get_children(parent):
            children = SubCategory.objects.filter(parent=parent)
            if children:
                return [
                    {
                        "id": child.id,
                        "name": child.name,
                        "description": child.description,
                        # "image": request.build_absolute_uri(child.image) if child.image else None,
                        "children": get_children(child),
                    }
                    for child in children
                ]
            return []

        serialized_categories = [
            {
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "children": get_children(category),
            }
            for category in categories
        ]

        response_data = {"StatusCode": 6000, "data": serialized_categories}
        return Response({"app_data": response_data}, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "data": {"message": "Category does not exist"},
        }
        return Response({"app_data": response_data}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@permission_classes((AllowAny,))
def category_tree(request):
    try:
        categories = Category.objects.all()

        def get_children(parent):
            if isinstance(parent, Category):
                children = SubCategory.objects.filter(
                    category=parent, parent__isnull=True
                )
            elif isinstance(parent, SubCategory):
                children = SubCategory.objects.filter(parent=parent)
            else:
                return []

            if children:
                return [
                    {
                        "id": child.id,
                        "name": child.name,
                        "description": child.description,
                        "children": get_children(child),
                    }
                    for child in children
                ]
            return []

        def serialize_category(category):
            return {
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "children": get_children(category),
            }

        serialized_categories = [
            serialize_category(category) for category in categories
        ]

        response_data = {"StatusCode": 6000, "data": serialized_categories}
        return Response({"app_data": response_data}, status=status.HTTP_200_OK)

    except Category.DoesNotExist:
        response_data = {"StatusCode": 6001, "data": {"message": "No categories exist"}}

    except Exception as e:
        # Handle other exceptions
        errType = e.__class__.__name__
        errors = {errType: traceback.format_exc()}
        response_data = {
            "status": 6001,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
            "response": errors,
        }

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
def product_list_by_price_range(request):
    try:
        filter_serializer = ProductFilterSerializer(data=request.GET)
        filter_serializer.is_valid(raise_exception=True)

        min_price = filter_serializer.validated_data.get("min_price")
        max_price = filter_serializer.validated_data.get("max_price")

        print(f"Received min_price: {min_price}, max_price: {max_price}")

        if min_price is not None and max_price is not None:
            products = Product.objects.filter(
                purchase_price__gte=min_price, purchase_price__lte=max_price
            )

            serializer = ProductListByPurchasePriceSerializer({"message": products})
            response_data = {"StatusCode": 6000, "message": {"data": serializer.data}}

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {"error": "Provide both min_price and max_price parameters"},
            }
            return Response({"app_data": response_data}, status=status.HTTP_200_OK)

    except serializers.ValidationError as e:
        error_message = f"Invalid parameter: {e}"
        response_data = {"StatusCode": 6001, "data": {"error": error_message}}
        return Response({"app_data": response_data}, status=status.HTTP_200_OK)

    except Exception as e:
        errType = e.__class__.__name__
        errors = {errType: str(e), "traceback": traceback.format_exc()}

        response_data = {
            "status": 6000,
            "api": request.get_full_path(),
            "request": request.data,
            "response": errors,
        }

        return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
def new_arrivals(request):
    try:
        new_arrival_threshold = datetime.now() - timedelta(days=7)
        new_arrival_products = Product.objects.filter(
            created_at__gte=new_arrival_threshold
        )
        serialized_products = []
        for product in new_arrival_products:
            serialized_products.append(
                {
                    "name": product.name,
                    "description": product.description,
                    "price": str(product.price),
                    "offers": product.offers,
                    "brand": product.brand.name if product.brand else None,
                    "subcategory": (
                        product.subcategory.name if product.subcategory else None
                    ),
                    "specs": product.specs,
                    "status": product.status,
                    "purchase_price": str(product.purchase_price),
                    "created_at": str(product.created_at),
                }
            )

        response_data = {
            "status": "success",
            "message": "New arrivals fetched successfully",
            "data": serialized_products,
        }

        return Response({"app_data": response_data}, status=status.HTTP_200_OK)

    except Exception as e:
        # Handle exceptions
        error_message = str(e)
        response_data = {
            "status": "error",
            "message": f"Error fetching new arrivals: {error_message}",
        }

        return Response(
            {"app_data": response_data}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@permission_classes((AllowAny,))
def view_attribute(request):
    try:
        instances = Attribute.objects.all()
        serializer = ViewAttributesSerializer(
            instances, context={"request": request}, many=True
        ).data
        response_data = {"StatusCode": 6000, "data": serializer}
    except Exception as e:
        # Handle exceptions
        error_message = str(e)
        response_data = {
            "status": "error",
            "message": f"Error fetching new arrivals: {error_message}",
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
def get_related_product(request):
    try:
        product_id = request.GET.get("product_id")
        if product_id:
            product = Product.objects.get(pk=product_id)
            instances = Product.objects.filter(product_code=product.product_code)
            serialized = ProductViewSerializer(
                instances, many=True, context={"request": request}
            ).data
            response_data = {"StatusCode": 6000, "data": serialized}
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {"message": "product_id is required"},
            }
    except Exception as e:
        # Handle exceptions
        error_message = str(e)
        response_data = {
            "status": "error",
            "message": f"Error fetching new arrivals: {error_message}",
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


# @api_view(["POST"])
# @permission_classes((AllowAny,))
# def add_new_attribute(request):
#     try:
#         transaction.set_autocommit(False)
#         serialized = AddAttributesSerializer(data=request.data)
#         if serialized.is_valid():
#             attribute = request.data["attribute"]
#             attribute_value = request.data["attribute_value"]
#             if not Attribute.objects.filter(attribute=attribute,attribute_value=attribute_value).exists():
#                 attribute = Attribute.objects.create(
#                     attribute=attribute,
#                     attribute_value=attribute_value
#                 )
#                 response_data = {
#                     "StatusCode":6000,
#                     "data":{
#                         "message":"Succesfully added attribute"
#                     }
#                 }
#                 transaction.commit()
#             else:
#                 response_data = {
#                     "StatusCode":6001,
#                     "data":{
#                         "message":"This attribute already exists."
#                     }
#                 }
#         else:
#             response_data = {
#                 "StatusCode": 6001,
#                 "data": generate_serializer_errors(serialized.errors)
#             }
#     except Exception as e:
#         # Handle exceptions
#         error_message = str(e)
#         response_data = {
#             'status': 'error',
#             'message': f'Error fetching new arrivals: {error_message}',
#         }
#     return Response({'app_data': response_data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
def add_new_attribute(request):
    try:
        transaction.set_autocommit(False)
        try:
            type_name = request.data[
                "name"
            ]  # Corrected variable name to avoid conflicts
        except KeyError:
            type_name = None
        try:
            values = request.data["values"]
        except KeyError:
            values = None

        if type_name and values:
            if not AttributeType.objects.filter(name=type_name).exists():
                attribute_type = AttributeType.objects.create(name=type_name)

                for value in values:
                    attribute_description = AttributeDescription.objects.create(
                        attribute_type=attribute_type, value=value
                    )
                transaction.commit()
                response_data = {
                    "StatusCode": 6000,
                    "message": "Attributes created successfully",
                }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "data": {"message": "Attribute already exists"},
                }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {"message": "name and values are required"},
            }

        transaction.commit()
    except Exception as e:
        transaction.rollback()
        # Handle exceptions
        error_message = str(e)
        response_data = {
            "StatusCode": 500,  # Adjust status code as needed
            "message": f"Error creating attributes: {error_message}",
        }

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
def addProductNew(request):
    try:
        transaction.set_autocommit(False)
        serialized = ProductSerializer(data=request.data)
        if serialized.is_valid():
            subcategory_id = request.data["subcategory_id"]
            actual_price = request.data["price"]
            selling_price = request.data["price"]
            gst_price = request.data["gst_price"]
            return_in = request.data["return_in"]
            name = request.data["name"]
            description = request.data["name"]
            referal_amount = request.data["referal_amount"]
            try:
                offer = request.data["offer"]
            except:
                offer = None
            try:
                width = request.data["width"]
            except:
                width = None
            try:
                height = request.data["height"]
            except:
                height = None
            try:
                weight = request.data["weight"]
            except:
                weight = None
            try:
                length = request.data["length"]
            except:
                length = None
            try:
                attributes = request.data["attributes"]
            except:
                attributes = None
            try:
                images = request.data["images"]
            except:
                images = request.data["images"]
            try:
                product_code = request.data["product_code"]
            except:
                product_code = ""
            try:
                gst_price = request.data["gst_price"]
            except:
                gst_price = ""
            try:
                cashback = request.data["cashback"]
            except:
                cashback = 0
            if attributes and images:
                if SubCategory.objects.filter(pk=subcategory_id).exists():
                    product = Product.objects.create(
                        sub_category=SubCategory.objects.get(pk=subcategory_id),
                        name=name,
                        description=description,
                        actual_price=actual_price,
                        selling_price=selling_price,
                        price=selling_price,
                        return_in=return_in,
                        referal_Amount=referal_amount,
                        cashback = cashback,
                        offer=offer,
                        width=width,
                        height=height,
                        weight=weight,
                        length=length,
                        gst_price=gst_price,
                    )
                    # serialized.save()
                    for attribute in attributes:
                        print(attribute, "")
                        attribute_description = AttributeDescription.objects.get(
                            pk=attribute.get("attributeDescription")
                        )
                        product_attributes = ProductAttribute.objects.create(
                            product=product,
                            attribute_description=attribute_description,
                            quantity=attribute.get("quantity", 0),
                        )
                    for image in images:
                        product_image = ProductImages.objects.create(
                            product=product,
                            image=image.get("image"),
                            thumbnail=image.get("thumbnail"),
                        )
                    if product_code:
                        product.product_code = product_code
                        product.is_parent = False
                        product.save()
                    transaction.commit()

                    instances = Product.objects.filter(
                        product_code=product.product_code
                    )
                    serialized = ProductCodeSerializer(
                        instances, context={"request": request}, many=True
                    ).data
                    response_data = {
                        "StatusCode": 6000,
                        "data": {"message": "Success", "products": serialized},
                    }
                else:
                    response_data = {
                        "StatusCode": 6001,
                        "data": {
                            "message": "Invalid Sub category",
                        },
                    }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "data": {"message": "Attribute and images are required"},
                }
        else:
            # Handle validation errors
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "message": "Failed",
                    "errors": generate_serializer_errors(serialized.errors),
                },
            }
    except Exception as e:
        transaction.rollback()
        # Handle exceptions
        error_message = str(e)
        response_data = {
            "StatusCode": 500,  # Adjust status code as needed
            "message": f"Error creating attributes: {error_message}",
        }

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["POST"])
def editProduct(request):
    try:
        id = request.data["id"]
        if Product.objects.filter(pk=id).exists():
            product = Product.objects.get(pk=id)
            product.name = request.data["name"]
            product.description = request.data["description"]
            product.product_sku = request.data["product_sku"]
            product.actual_price = request.data["actual_price"]
            product.selling_price = request.data["selling_price"]
            product.return_in = request.data["return_in"]
            product.referal_Amount = request.data["referal_Amount"]
            product.weight = request.data["weight"]
            product.height = request.data["height"]
            product.length = request.data["length"]
            product.width = request.data["width"]
            product.gst_price = request.data["gst_price"]
            existing_images = ProductImages.objects.filter(product=product)
            existing_images.delete()
            product.save()
            attributes = request.data["attribute"]
            thumbnail = request.data["thumbnail"]
            images = request.data["images"]
            if request.data["sub_category"]:
                sub_pk= request.data["sub_category"]
                if SubCategory.objects.filter(pk=sub_pk).exists():
                    sub_category = SubCategory.objects.get(pk=sub_pk)
                    product.sub_category = sub_category
            product_attribute = ProductAttribute.objects.filter(product=product)
            product_attribute.delete()
            
            for attribute in attributes:
                try:
                    if AttributeDescription.objects.filter(pk=attribute["attributeDescription"]).exists():
                        attribute_description = AttributeDescription.objects.get(pk=attribute["attributeDescription"])
                        attribute_obj = ProductAttribute.objects.create(
                                product=product,
                                attribute_description=attribute_description,
                                quantity=attribute["quantity"]
                            )
                except Exception as e:
                    response_data = {
                        "StatusCode":6001,
                        "data":{
                            "message":str(e)
                        }
                    }
            
            new_images = [ProductImages(product=product, image=img["image"], thumbnail=False) for img in images]
            ProductImages.objects.bulk_create(new_images)

            if thumbnail:
                ProductImages.objects.create(
                    product = product,
                    image = thumbnail,
                    thumbnail = True
                )
            response_data = {
                "StatusCode":6000,
                "data":{
                    "message":"updated product"
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
        transaction.rollback()
        # Handle exceptions
        error_message = str(e)
        response_data = {
            "StatusCode": 500,  # Adjust status code as needed
            "message": f"Error creating attributes: {error_message}",
        }

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)

@api_view(["GET"])
@group_required(
    [
        "admin",
    ]
)
def get_parents(request):
    response_data = {"StatusCode": 6000}
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
def viewAttributeType(request):
    try:
        instance = AttributeType.objects.all()
        print(instance)
        serialized = AttributeTypeSerializer(
            instance, context={"request": request}, many=True
        ).data
        response_data = {"StatusCode": 6000, "data": serialized}
    except Exception as e:
        transaction.rollback()
        # Handle exceptions
        error_message = str(e)
        response_data = {
            "StatusCode": 500,  # Adjust status code as needed
            "message": f"Error creating attributes: {error_message}",
        }

    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
def viewAttributeDescription(request, pk):
    try:
        attribute_type = AttributeType.objects.get(pk=pk)
        instances = AttributeDescription.objects.filter(attribute_type=attribute_type)
        serialized = AttributeDescriptionSerializer(
            instances, context={"request": request}, many=True
        ).data

        response_data = {"StatusCode": 6000, "data": serialized}
    except Exception as e:
        transaction.rollback()
        # Handle exceptions
        error_message = str(e)
        response_data = {
            "StatusCode": 500,  # Adjust status code as needed
            "message": f"Error creating attributes: {error_message}",
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@group_required(["admin"])
def productSingle(request, pk):
    try:
        transaction.set_autocommit(False)
        if Product.objects.filter(pk=pk).exists():
            instance = Product.objects.get(pk=pk)
            serialized = ProductAdminSerializer(
                instance, context={"request": request}
            ).data
            response_data = {"StatusCode": 6000, "data": serialized}
            transaction.commit()
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {"message": "product not exists"},
            }
    except Exception as e:
        error_message = str(e)
        response_data = {
            "status": "error",
            "message": f"Error fetching new arrivals: {error_message}",
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@group_required(
    [
        "admin",
    ]
)
def delete_product(request, pk):
    if Product.objects.filter(pk=pk).exists():
        product = Product.objects.get(pk=pk)
        product.delete()
        response_data = {
            "StatusCode": 6000,
            "data": {"message": "successfully deleted product"},
        }
    else:
        response_data = {"StatusCode": 6001, "data": {"message": " product not found"}}
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@group_required(
    [
        "admin",
    ]
)
def add_to_featured(request, pk):
    try:
        featured = request.data.get("featured", None)
        if featured is not None:
            if Product.objects.filter(pk=pk).exists():
                product = Product.objects.get(pk=pk)
                product.featured = featured
                product.save()
                response_data = {
                    "StatusCode": 6000,
                    "data": {"message": "added product to featured"},
                }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "data": {"message": "product not found"},
                }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {"message": "featured is required"},
            }
    except Exception as e:
        error_message = str(e)
        response_data = {
            "status": "error",
            "message": f"Error adding product to featured: {error_message}",
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@group_required(["admin"])
def add_to_flashsale(request, pk):
    try:
        if Product.objects.filter(pk=pk).exists():
            product = Product.objects.get(pk=pk)
            flash_sale = not product.flash_sale
            product.flash_sale = flash_sale
            product.save()
            response_data = {
                "StatusCode": 6000,
                "data": {"message": "successfully added to flash sale"},
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {"message": "product not found"},
            }
    except Exception as e:
        error_message = str(e)
        response_data = {
            "status": "error",
            "message": f"Error adding product to flash sale: {error_message}",
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
def viewProductCode(request):
    try:
        instances = Product.objects.filter(is_parent=True)
        serialized = ProductCodeSerializer(
            instances, many=True, context={"request": request}
        ).data
        response_data = {"StatusCode": 6001, "data": serialized}
    except Exception as e:
        error_message = str(e)
        response_data = {
            "status": "error",
            "message": f"Error fetching new arrivals: {error_message}",
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
def get_varients(request):
    try:
        product_code = request.GET.get("product_code", None)
        instances = Product.objects.filter(product_code=product_code)
        serialized = ProductWithCodeSerializer(
            instances, many=True, context={"request": request}
        ).data
        response_data = {"StatusCode": 6000, "data": serialized}
    except Exception as e:
        error_message = str(e)
        response_data = {
            "status": "error",
            "message": f"Error fetching new arrivals: {error_message}",
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@group_required(["admin"])
def inventory(request):
    try:
        type = request.GET.get("type")
        search = request.GET.get("search")
        if type == "all":
            instances = Product.objects.annotate(
                total_quantity=Sum("productattribute__quantity")
            )
        elif type == "out_of_stock":
            instances = Product.objects.annotate(
                total_quantity=Sum("productattribute__quantity")
            ).filter(total_quantity=0)
        elif type == "low_stock":
            instances = Product.objects.annotate(
                total_quantity=Sum("productattribute__quantity")
            ).filter(total_quantity__gt=0, total_quantity__lte=20)
        else:
            instances = Product.objects.all()
        if search:
            instances = instances.filter(name__icontains=search)
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
        serialized = InventorySerializers(
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
        error_message = str(e)
        response_data = {
            "status": "error",
            "message": f"Error fetching new arrivals: {error_message}",
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
def view_stock(request, pk):
    try:
        if Product.objects.filter(pk=pk).exists():
            product = Product.objects.get(pk=pk)
            instances = ProductAttribute.objects.filter(product=product)

            serialized = ProductStockSerialier(instances, many=True)
            response_data = {"StatusCode": 6000, "data": serialized.data}
        else:
            response_data = {"StatusCode": 6001, "data": {"message": "not exists"}}
    except Exception as e:
        error_message = str(e)
        response_data = {
            "status": "error",
            "message": f"Error fetching new arrivals: {error_message}",
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["POST"])
def update_quantity(request):
    try:
        datas = request.data.get("datas", [])
        for data in datas:
            product_attribute = get_object_or_404(ProductAttribute, pk=data["id"])
            product_attribute.quantity = int(data["quantity"])
            product_attribute.save()
        
        response_data = {
            "status": 6000,
            "data": {
                "message": "Successfully changed"
                },
        }
        status_code = status.HTTP_200_OK
    except ProductAttribute.DoesNotExist:
        response_data = {
            "status": "error",
            "message": "Product attribute not found.",
        }
        status_code = status.HTTP_404_NOT_FOUND
    except Exception as e:
        error_message = str(e)
        response_data = {
            "status": "error",
            "message": f"Error updating quantities: {error_message}",
        }
        status_code = status.HTTP_400_BAD_REQUEST

    return Response({"app_data": response_data}, status=status_code)


@api_view(["POST"])
def update_publish(request, pk):
    try:
        published = request.data["published"]
        if Product.objects.filter(pk=pk).exists():
            product = Product.objects.get(pk=pk)
            product.published = published
            product.save()
            response_data = {
                "StatusCode": 6000,
                "data": {"message": "product published succesfully"},
            }
    except Exception as e:
        error_message = str(e)
        response_data = {
            "status": "error",
            "message": f"Error updating quantities: {error_message}",  # Changed the error message
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
def viewSubCategoryItem(request, pk):
    try:
        if not SubCategory.objects.filter(pk=pk).exists():
            response_data = {
                "StatusCode": 6001,
                "data": {"message": "no sub category found"},
            }
            return Response({"app_data": response_data}, status=status.HTTP_200_OK)
        sub_category = SubCategory.objects.get(pk=pk)
        response_data = {
            "StatusCode": 6000,
            "data": {
                "id": sub_category.pk,
                "name": sub_category.name,
                "description": sub_category.description,
                "image": sub_category.image,
            },
        }
    except Exception as e:
        error_message = str(e)
        response_data = {
            "status": "error",
            "message": f"Error updating quantities: {error_message}",  # Changed the error message
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["post"])
def editSubCategoryItem(request, pk):
    try:
        try:
            name = request.data["name"]
        except:
            name = None
        try:
            description = request.data["description"]
        except:
            description = None
        try:
            image =request.data["image"]
        except:
            image = None
        if not SubCategory.objects.filter(pk=pk).exists():
            response_data = {
                "StatusCode": 6001,
                "data": {"message": "sub category does not exist"},
            }
            return Response({"app_data": response_data}, status=status.HTTP_200_OK)
        sub_category = SubCategory.objects.get(pk=pk)
        if name:
            sub_category.name = name
        if description:
            sub_category.description = description
        if image:
            sub_category.image = image
            
        sub_category.save()
        response_data = {"SatusCode": 6000, "data": {"message": "success updated"}}
    except Exception as e:
        error_message = str(e)
        response_data = {
            "status": "error",
            "message": f"Error updating quantities: {error_message}",  # Changed the error message
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
def attribute_detail(request, pk):
    try:
        if not AttributeType.objects.filter(pk=pk).exists():
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "message": "failed",
                    "error": f"Attribute with id={pk} is not found.",
                },
            }
            return Response({"app_data": response_data}, status=status.HTTP_200_OK)
        instance = AttributeType.objects.get(pk=pk)
        serialized = AttributeViewSerializer(instance).data

        response_data = {"StatusCode": 6000, "data": serialized}
    except Exception as e:
        error_message = str(e)
        response_data = {
            "status": "error",
            "message": f"Error updating quantities: {error_message}",  # Changed the error message
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["POST"])
# @group_required(["admin"])
@permission_classes((AllowAny,))
def edit_attribute(request):
    data = request.data
    attribute_id = data["id"]
    attribute_name = data["name"]
    attribute_values = data["attribute_description"]
    if not AttributeType.objects.filter(pk=attribute_id).exists():
        response_data = {"StatusCode": 6001, "data": {"message": "attribute not found"}}
        return Response({"app_data": response_data}, status=status.HTTP_200_OK)
    attribute = AttributeType.objects.get(pk=attribute_id)
    attribute.name = attribute_name
    attribute.save()
    attr_desc = AttributeDescription.objects.filter(attribute_type=attribute).delete()
    for value in attribute_values:
        if not value.get("value") or value["value"].strip() == "":
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "message": "One or more attribute descriptions have an empty value."
                },
            }
            return Response({"app_data": response_data}, status=status.HTTP_400_BAD_REQUEST)
       
        AttributeDescription.objects.create(
            attribute_type=attribute, value=value["value"]
        )
    response_data = {
        "StatusCode": 6000,
        "data": {"message": "attribute updated successfully"},
    }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


# @api_view(["DELETE"])
# @permission_classes((AllowAny,))
# def delete_attribute(request, pk):
#     try:
#         if not AttributeType.objects.filter(pk=pk).exists():
#             response_data = {
#                 "StatusCode": 6001,
#                 "data": {"message": "attribute not found with this id"},
#             }
#             return Response({"app_data": response_data}, status=status.HTTP_200_OK)
#         attribute = AttributeType.objects.get(pk=pk)
#         attribute.delete()
#         response_data = {
#             "StatusCode": 6000,
#             "data": {"message": "attribute deleted successfully"},
#         }
#         return Response({"app_data": response_data}, status=status.HTTP_200_OK)
#     except Exception as e:
#         error_message = str(e)
#         response_data = {
#             "status": "error",
#             "message": f"Error updating quantities: {error_message}",  # Changed the error message
#         }
#         return Response({"app_data": response_data}, status=status.HTTP_200_OK)
