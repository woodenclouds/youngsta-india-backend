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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@api_view(["GET"])
@group_required(["admin"])
def admin_product(request):
    try:
        instance = Product.objects.all()
        paginator = Paginator(instance, 8)
        page = request.GET.get('page')
        try:
            farmers = paginator.page(page)
        except PageNotAnInteger:
            farmers = paginator.page(1)
        except EmptyPage:
            farmers = paginator.page(paginator.num_pages)

        next_page_number = 1
        has_next_page = False
        if farmers.has_next():
            has_next_page = True
            next_page_number = farmers.next_page_number()

        has_previous_page = False
        previous_page_number = 1
        if farmers.has_previous():
            has_previous_page = True
            previous_page_number = farmers.previous_page_number()
        serialized = ProductAdminViewSerializer(
            instance,
            many = True
        ).data
        response_data = {
            "StatusCode":6000,
            "data":serialized,
            'pagination_data': {
                'current_page': farmers.number,
                'has_next_page': has_next_page,
                'next_page_number': next_page_number,
                'has_previous_page': has_previous_page,
                'previous_page_number': previous_page_number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'first_item': farmers.start_index(),
                'last_item': farmers.end_index(),
            },
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
            highest_order = Category.objects.aggregate(Max('position'))['position__max']

            # Set the order for the new category to be the next sequential number
            order = highest_order + 1 if highest_order is not None else 1

            category = Category.objects.create(
                name=name,
                description=description,
                image=image,
                cat_id=cat_id,
                position=order
            )
            transaction.commit()
            print(cat_id)
            response_data = {
                "StatusCode": 6000,
                "data": {
                    "message": "category created successfully"
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


@api_view(["GET"])
@permission_classes((AllowAny,))
def categories(request):
    try:
        instances = Category.objects.order_by('position')
        serialized_instances = []

        for instance in instances:
            if instance.is_deleted == False: 
                serialized_instances.append(ViewCategorySerializer(instance).data)

        response_data = {
            "StatusCode": 6000,
            "data": serialized_instances
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
                "message": "Category updated successfully"
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": generate_serializer_errors(serializer.errors)
            }
    except Category.DoesNotExist:
        response_data = {
            "StatusCode": 6002,
            "data": {"message": "Category not found"}
        }
    except Exception as e:
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



@api_view(["PUT", "PATCH"])
@permission_classes((AllowAny,))
def editCategoryPosition(request, pk):
    try:
        category = Category.objects.get(id=pk)
        serializer = EditCategoryPositionSerializer(instance=category, data=request.data)

        if serializer.is_valid():
            new_position = serializer.validated_data.get('position')

            # Check if the new position is within the valid range
            total_categories = Category.objects.count()
            if 1 <= new_position <= total_categories:
                with transaction.atomic():
                    current_position = category.position

                    # Shift categories below the target position up
                    if current_position < new_position:
                        Category.objects.filter(
                            position__gt=current_position,
                            position__lte=new_position
                        ).update(position=models.F('position') - 1)
                    # Shift categories above the target position down
                    elif current_position > new_position:
                        Category.objects.filter(
                            position__lt=current_position,
                            position__gte=new_position
                        ).update(position=models.F('position') + 1)

                    # Update the position of the current category
                    category.position = new_position
                    category.save()

                    response_data = {
                        "StatusCode": 6000,
                        "data": {
                            "message": f"Category position updated successfully to {new_position}"
                        }
                    }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "data": {"message": "Invalid position value"}
                }
        else:
            response_data = {
                "StatusCode": 6002,
                "data": generate_serializer_errors(serializer.errors)
            }
    except Category.DoesNotExist:
        response_data = {
            "StatusCode": 6003,
            "data": {"message": "Category not found"}
        }
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
            "response": {"error": "An error occurred while updating the category position"}
        }

    return Response({'app_data': response_data}, status=status.HTTP_200_OK)




@api_view(["DELETE"])
@group_required(["admin"])
def deleteCategory(request, pk):
    try:
        category = Category.objects.get(pk=pk)
        category.is_deleted = True
        category.save()

        # Update the order of all categories
        all_categories = Category.objects.annotate(
            is_deleted_int=Case(When(is_deleted=True, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
            ).order_by('is_deleted_int', 'position')

        for i, current_category in enumerate(all_categories, start=1):
            current_category.position = i
            current_category.save()
        response_data = {
            "StatusCode": 6000,
            "data" : {
                "message" : f"{category.name} deleted successfully"
            }
        }
    except Category.DoesNotExist:
        response_data = {
            "StatusCode": 6001,
            "data": {"message": "Category not found"}
        }
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
            "response": {"error": "An error occurred while deleting the category"}
        }

    return Response({'app_data': response_data}, status=status.HTTP_200_OK)





                
@api_view(["POST"])
@group_required(["admin"])
def addProduct(request):
    try:
        transaction.set_autocommit(False)
        serialized = AddProductSerializer(data=request.data)
        if serialized.is_valid():
            name = request.data["name"]
            description = request.data["description"]
            subcategoryId = request.data['subcategory_id']
            price = request.data["price"]
            offers = request.data["offers"]
            purchase_price = request.data["purchase_price"]
            brandId = request.data["brand_id"]
            error = False
            if not SubCategory.objects.filter(pk=subcategoryId).exists():
                error = True
                response_data = {
                    "StatusCode":6001,
                    "data":{
                        "message":"sub category not exist"
                    }
                }
            if not Brand.objects.filter(pk=brandId).exists():
                error = True
                response_data = {
                    "StatusCode":6001,
                    "data":{
                        "message":"brand not exist"
                    }
                }
            if Product.objects.filter(name=name).exists():
                error = True
                response_data = {
                    "StatusCode":6001,
                    "data":{
                        "message":"product already exists",
                    }
                }
            if not error:
                subcategory = SubCategory.objects.get(pk=subcategoryId)
                brand = Brand.objects.get(pk=brandId)
                product = Product.objects.create(name=name, description=description, subcategory=subcategory, price=price,offers=offers,purchase_price=purchase_price,brand=brand)
                transaction.commit()
                response_data = {
                    "StatusCode":6000,
                    "data":{
                        "message": f"{product.name} created succesfully",
                        "product_name":product.name,
                        "id":product.id
                    }
                }
        else:
            response_data = {
                    "StatusCode": 6001,
                    "data": generate_serializer_errors(serialized._errors)
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
@group_required(["admin"])
def addVarient(request,pk):
    try:
        transaction.set_autocommit(False)
        error = False
        message = ""
        datas = request.data
        if not Product.objects.filter(pk=pk).exists():
            error =True
            message = "Product dous not exist"
        if not error:
            product = Product.objects.get(pk=pk)
            for data in datas:
                images = data.get('images')
                attributes = data.get('attributes')
                print(attributes,"_____atri___obj")
                product_varient = ProductVarient.objects.create(
                    product = product,
                    thumbnail = images[0]
                )
                for image in images:
                    print(image,"______image")
                    product_image = ProductImages.objects.create(
                        image = image,
                        product_varient = product_varient
                    )

                for attribute in attributes:
                    print(attribute,"test______test")
                    attribute_obj = Attribute.objects.create(
                        attribute = attribute["attribute"],
                        attribute_value = attribute["attribute_value"],
                        quantity = attribute["quantity"]
                    )
            transaction.commit()
            response_data={
                "StatusCode":6000,
                "data":{
                    "message":"Succesfully created varient"
                }
            }
        else:
            response_data = {
                "StatusCode":6001,
                "data":{
                    "message":message
                }
            }
    except Exception as e:
        transaction.rollback()
        errType = e.__class__.__name__
        errors = {
            errType: traceback.format_exc()
        }
        response_data = {
            "status": 6001,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
            "response": errors
        }

    return Response({'app_data': response_data}, status=status.HTTP_200_OK)


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
                response_data={
                    "StatusCode":6001,
                    "data":"brand with this name already exists"
                }
            else:  
                brand= Brand.objects.create(
                    name = name,
                    description = description,
                    image = image
                ) 
                transaction.commit()
                response_data = {
                    "StatusCode":6000,
                    "data":{
                        "message":f"{brand.name} created succesfully"
                    }
                }         
        else:
            response_data = {
                    "StatusCode": 6001,
                    "data": generate_serializer_errors(serialized._errors)
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

        response_data = {
            "StatusCode": 6000,
            "data": serialized_instances
        }
    except Exception as e:
        transaction.rollback()
        errType = e._class.name_
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
                "message": "brand updated successfully"
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": generate_serializer_errors(serializer.errors)
            }
    except Category.DoesNotExist:
        response_data = {
            "StatusCode": 6002,
            "data": {"message": " not found"}
        }
    except Exception as e:
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
            "data" : {
                "message" : f"{brand.name} deleted Successfully"
            }
        }
    except Brand.DoesNotExist:
        response_data = {
            "StatusCode": 6001,
            "data": {"message": "Category not found"}
        }
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
            "response": {"error": "An error occurred while deleting the category"}
        }

    return Response({'app_data': response_data}, status=status.HTTP_200_OK)


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
                    "attribute": serializer.data
                }
            }
            return Response({'app_data': response_data}, status=status.HTTP_201_CREATED)
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
            "message": str(e),
        }
    return Response({'app_data': response_data}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def listAttributes(request):
    try:
        instances = Attribute.objects.all()
        serialized_instances = []

        for instance in instances:
            if not instance.is_deleted:  # Check if 'is_deleted' is False
                serialized_instances.append(AttributeSerializer(instance).data)

        response_data = {
            "StatusCode": 6000,
            "data": serialized_instances
        }
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
        return Response({'app_data': response_data}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'app_data': response_data}, status=status.HTTP_200_OK)




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
                "message": "Attribute updated successfully"
            }
            return Response({'app_data': response_data}, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 400,
                "data": serializer.errors,
                "message": "Invalid data"
            }
            return Response({'app_data': response_data}, status=status.HTTP_400_BAD_REQUEST)

    except Attribute.DoesNotExist:
        response_data = {
            "StatusCode": 404,
            "message": "Attribute does not exist"
        }
        return Response({'app_data': response_data}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
        }
        return Response({'app_data': response_data}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(["DELETE"])
@group_required(["admin"])
def deleteAttribute(request, pk):
    try:
        attribute = Attribute.objects.get(pk=pk)
        attribute.delete()  # Remove the attribute completely from the database
        response_data = {
            "StatusCode": 6000,
            "data": {
                "message": f"Attribute '{attribute.title}' deleted successfully"
            }
        }
    except Attribute.DoesNotExist:
        response_data = {
            "StatusCode": 6001,
            "data": {"message": "Attribute not found"}
        }
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
            "response": {"error": "An error occurred while deleting the attribute"}
        }

    return Response({'app_data': response_data}, status=status.HTTP_200_OK)


#-----------------Sub Category ----------------------------------------------------------------


@api_view(["POST"])
@group_required(["admin"])
def addSubcategory(request):
    try:
        transaction.set_autocommit(False)
        serialized = AddSubCategorySerializer(data=request.data)
        category_id = request.data["category"]
        parent_id = request.data.get("parent")  # Use get to avoid KeyError if "parent" is not present

        errors = []

        if not serialized.is_valid():
            errors.append(generate_serializer_errors(serialized._errors))

        if not Category.objects.filter(pk=category_id).exists():
            errors.append("Category does not exist.")

        if parent_id and not SubCategory.objects.filter(pk=parent_id).exists():
            errors.append("Parent SubCategory does not exist.")

        if errors:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "message": ", ".join(errors)
                    }
            }
        else:
            name = request.data["name"]
            description = request.data["description"]
            category = Category.objects.get(pk=category_id)

            if parent_id:
                parent = SubCategory.objects.get(pk=parent_id)
            else:
                parent = None

            # Get the highest existing position for SubCategory
            highest_position = SubCategory.objects.aggregate(Max('position'))['position__max']

            # Set the position for the new SubCategory to be the next sequential number
            position = highest_position + 1 if highest_position is not None else 1

            if not SubCategory.objects.filter(name=name, category=category).exists():
                sub_category = SubCategory.objects.create(
                    name=name,
                    description=description,
                    category=category,
                    parent=parent,
                    position=position
                )

                transaction.commit()
                response_data = {
                    "StatusCode": 6000,
                    "data": {
                        "message": f"{sub_category.name} successfully created"
                        }
                }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "data": {
                        "message": "Subcategory already exists"
                        }
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


@api_view(["GET"])
@permission_classes((AllowAny,))
def viewSubCategory(request, type):
    try:
        response_data = {}

        if type == "all":
            instances = SubCategory.objects.filter(is_deleted=False)
            serialized_instances = [ViewSubCategorySerializer(instance).data for instance in instances]
            response_data = {
                "StatusCode": 6000,
                "data": {
                    "message": serialized_instances
                }
            }
        elif SubCategory.objects.filter(pk=type, is_deleted=False).exists():
            instances = SubCategory.objects.filter(pk=type, is_deleted=False)
            serialized_instances = [ViewSubCategorySerializer(instance).data for instance in instances]
            response_data["sub_category_exists"] = {
                "StatusCode": 6000,
                "data": {
                    "message": serialized_instances
                }
            }
        elif SubCategory.objects.filter(category=type, is_deleted=False).exists():
            instances = SubCategory.objects.filter(category=type, is_deleted=False)
            serialized_instances = [ViewSubCategorySerializer(instance).data for instance in instances]
            response_data["sub_category_belongs_to_category"] = {
                "StatusCode": 6000,
                "data": {
                    "message": serialized_instances
                }
            }
        else:
            response_data["invalid_condition"] = {
                "StatusCode": 6001,
                "data": {
                    "message": "Invalid condition or Sub Category does not exist"
                }
            }

    except Exception as e:
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

@api_view(["PUT", "PATCH"])
@group_required(["admin"])
def editSubCategory(request, pk):
    try:
        subcategory = SubCategory.objects.get(id=pk)
        serializer = EditSubCategorySerializer(subcategory, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()

            response_data = {
                "StatusCode": 6000,
                "data": serializer.data,
                "message": "Subcategory updated successfully"
            }

        # Handle validation errors
        else:
            response_data = {
                "StatusCode": 6001,
                "data": serializer.errors
            }

    except SubCategory.DoesNotExist:
        response_data = {
            "StatusCode": 6002,
            "data": {"message": "Subcategory not found"}
        }
    except Exception as e:
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



@api_view(["DELETE"])
@group_required(["admin"])
def deleteSubCategory(request, pk):
    try:
        subcategory = SubCategory.objects.get(pk=pk)
        subcategory.is_deleted = True
        subcategory.save()

        # Update the order of all categories
        all_subcategories = SubCategory.objects.annotate(
            is_deleted_int=Case(When(is_deleted=True, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
            ).order_by('is_deleted_int', 'position')

        for i, current_subcategory in enumerate(all_subcategories, start=1):
            current_subcategory.position = i
            current_subcategory.save()
        response_data = {
            "StatusCode": 6000,
            "data" : {
                "message" : f"{subcategory.name} deleted successfully"
            }
        }
    except Category.DoesNotExist:
        response_data = {
            "StatusCode": 6001,
            "data": {"message": "Sub Category not found"}
        }
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
            "response": {"error": "An error occurred while deleting the category"}
        }

    return Response({'app_data': response_data}, status=status.HTTP_200_OK)



@api_view(["PUT", "PATCH"])
@permission_classes((AllowAny,))
def editSubCategoryPosition(request, pk):
    try:
        category = SubCategory.objects.get(id=pk)
        serializer = EditSubCategoryPositionSerializer(instance=category, data=request.data)

        if serializer.is_valid():
            new_position = serializer.validated_data.get('position')

            # Check if the new position is within the valid range
            total_categories = SubCategory.objects.count()
            if 1 <= new_position <= total_categories:
                with transaction.atomic():
                    current_position = category.position

                    # Shift categories below the target position up
                    if current_position < new_position:
                        SubCategory.objects.filter(
                            position__gt=current_position,
                            position__lte=new_position
                        ).update(position=models.F('position') - 1)
                    # Shift categories above the target position down
                    elif current_position > new_position:
                        SubCategory.objects.filter(
                            position__lt=current_position,
                            position__gte=new_position
                        ).update(position=models.F('position') + 1)

                    # Update the position of the current category
                    category.position = new_position
                    category.save()

                    response_data = {
                        "StatusCode": 6000,
                        "data": {
                            "message": f"Category position updated successfully to {new_position}"
                        }
                    }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "data": {
                        "message": "Invalid position value"
                        }
                }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": generate_serializer_errors(serializer.errors)
            }
    except SubCategory.DoesNotExist:
        response_data = {
            "StatusCode": 6001,
            "data": {
                "message": "Category not found"
                }
        }
    except Exception as e:
        response_data = {
            "status": 0,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
            "response": {"error": "An error occurred while updating the category position"}
        }

    return Response({'app_data': response_data}, status=status.HTTP_200_OK)


#-----------------Sub Category End----------------------------------------------------------------

#=========== Product =================================================================

@api_view(["POST"])
@group_required(["admin"])
def addProductItem(request,pk):
    try:
        transaction.set_autocommit(False)
        serialized = AddProductItemSerializer(data=request.data)
        error = False
        if not serialized.is_valid():
            error=True
            response_data = {
                    "StatusCode": 6001,
                    "data": generate_serializer_errors(serialized._errors)
                }
        if not Product.objects.filter(pk=pk).exists():
            response_data = {
                "StatusCode":6001,
                "data":{
                    "message":"product with this pk not exist"
                }
            }
        if not error:
            product = Product.objects.get(pk=pk)
            color = request.data["color"]
            stock = request.data["stock"]
            size = request.data["size"]
            images = request.data.get("images", [])
            print(images,"_________imag")
            product_item = ProductItem.objects.create(
                color = color,
                stock = stock,
                size = size,
                product = product
            )
            # for image in images:
            #     print(image,"_______image_______")
                # product_image = ProductImages.objects.create(
                #     product_item = product_item,
                #     image = image
                # )
            transaction.commit()
            response_data = {
                "StatusCode":6000,
                "data":{
                    "message":"created product item"
                }
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




#----------------------- Products -----------------------------------------
@api_view(["GET"])
@permission_classes((AllowAny,))
def viewProduct(request, type):
    try:
        response_data = {}

        if type == "all":
            instances = Product.objects.filter(is_deleted=False)
            serialized_instances = [ProductViewSerializer(instance).data for instance in instances]
            response_data = {
                "StatusCode": 6000,
                "data": serialized_instances
            }

        elif Product.objects.filter(id=type, is_deleted=False).exists():
            instances = Product.objects.filter(id=type, is_deleted=False)
            serialized_instances = [ProductViewSerializer(instance).data for instance in instances]
            response_data = {
                "StatusCode": 6000,
                "data": serialized_instances
            }             


        elif Product.objects.filter(brand__id=type, is_deleted=False).exists():
            
            instances = Product.objects.filter(brand__id=type, is_deleted=False)
            serialized_instances = [ProductViewSerializer(instance).data for instance in instances]
            response_data = {
                "StatusCode": 6000,
                "data": serialized_instances
            }             


        elif Product.objects.filter(subcategory__id=type, is_deleted=False).exists():
            instances = Product.objects.filter(subcategory__id=type, is_deleted=False)
            serialized_instances = [ProductViewSerializer(instance).data for instance in instances]
            response_data = {
                "StatusCode": 6000,
                "data": {
                    "message": serialized_instances
                }
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "message": "Product not found or deleted"
                }
            }

    except Exception as e:
        transaction.rollback()
        errType = e.__class__.__name__
        errors = {
            errType: traceback.format_exc()
        }
        response_data.update({
            "status": 6001,
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(e),
            "response": errors
        })

    return Response({'app_data': response_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
def product_list_by_price_range(request):
    try:
        filter_serializer = ProductFilterSerializer(data=request.GET)
        filter_serializer.is_valid(raise_exception=True)

        min_price = filter_serializer.validated_data.get('min_price')
        max_price = filter_serializer.validated_data.get('max_price')

        print(f"Received min_price: {min_price}, max_price: {max_price}")

        if min_price is not None and max_price is not None:
            products = Product.objects.filter(purchase_price__gte=min_price, purchase_price__lte=max_price)

            serializer = ProductListByPurchasePriceSerializer({'message': products})
            response_data = {
                "StatusCode": 6000,
                "message" : {
                    "data": serializer.data
                }
                
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                'data': {'error': 'Provide both min_price and max_price parameters'}
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    except serializers.ValidationError as e:
        error_message = f"Invalid parameter: {e}"
        response_data = {
            "StatusCode": 6001,
            'data': {'error': error_message}
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        errType = e.__class__.__name__
        errors = {
            errType: str(e),
            'traceback': traceback.format_exc()
        }

        response_data = {
            "status": 6000,
            "api": request.get_full_path(),
            "request": request.data,
            "response": errors
        }

        return Response({'app_data': response_data}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)