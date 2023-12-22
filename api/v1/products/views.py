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

@api_view(["GET"])
@group_required(["admin"])
def admin_product(request):
    try:
        isinstance = Product.objects.all()
        serialized = ProductAdminViewSerializer(
            isinstance,
            many = True
        ).data
        response_data = {
            "StatusCode":6000,
            "data":serialized
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
            highest_order = Category.objects.aggregate(Max('orders'))['orders__max']

            # Set the order for the new category to be the next sequential number
            order = highest_order + 1 if highest_order is not None else 1

            category = Category.objects.create(
                name=name,
                description=description,
                image=image,
                cat_id=cat_id,
                orders=order
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
        instances = Category.objects.all()
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
        # Get the existing category instance
        category = Category.objects.get(id=pk)
        print(category)
        # Deserialize the request data
        serializer = EditCategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            name = request.data.get("name")
            description = request.data.get("description")
            image = request.data.get("image")
            category.name = name
            category.description = description
            category.image = image
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
def editCategoryOrder(request, pk):
    try:
        category = Category.objects.get(id=pk)
        serializers = EditCategoryOrderSerializer(data=request.data)
        if serializers.is_valid():
            new_order = int(request.data.get('orders'))

            # Get the current order of the category
            current_order = category.orders

            # Update the order of the specified category
            category.orders = new_order
            category.save()

            # Update the order of other categories after the specified category
            categories_to_update = Category.objects.filter(is_deleted=False, orders__gt=current_order)
            for other_category in categories_to_update:
                other_category.orders += 1
                other_category.save()

            response_data = {
                "StatusCode": 6000,
                "data": {"message": "Category order updated successfully"}
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": generate_serializer_errors(serializers.errors)
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
            ).order_by('is_deleted_int', 'orders')

        for i, current_category in enumerate(all_categories, start=1):
            current_category.orders = i
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
                        "message":"product already exists"
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
                        "message": f"{product.name} created succesfully"
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



@api_view(["POST"])
@group_required(["admin"])
def addSubcategory(request):
    try:
        transaction.set_autocommit(False)
        serialized = AddSubCategorySerializer(data=request.data)
        category_id = request.data["category"]
        parent_id = request.data.get("parent")  # Use get to avoid KeyError if "parent" is not present
        error = False

        if not serialized.is_valid():
            error = True
            response_data = {
                "StatusCode": 6001,
                "data": generate_serializer_errors(serialized._errors)
            }

        if not Category.objects.filter(pk=category_id).exists():
            error = True
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "message": "category not exist"
                }
            }

        if parent_id and not SubCategory.objects.filter(pk=parent_id).exists():
            error = True
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "message": "parent not exist"
                }
            }

        if not error:
            name = request.data["name"]
            description = request.data["description"]
            category = Category.objects.get(pk=category_id)

            if parent_id:
                parent = SubCategory.objects.get(pk=parent_id)
            else:
                parent = None

            if not SubCategory.objects.filter(name=name, category=category).exists():
                sub_category = SubCategory.objects.create(
                    name=name,
                    description=description,
                    category=category,
                    parent=parent
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
                        "message": "subcategory already exists"
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
def viewSubCategory(request):
    try:
        instances = SubCategory.objects.filter(is_deleted=False)
        serialized_instances = []

        for instance in instances:
            serialized_instance = ViewSubCategorySerializer(instance).data
            serialized_instances.append(serialized_instance)

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
def editSubCategory(request, pk):
    try:
        subcategory = SubCategory.objects.get(id=pk)
        serializer = EditSubCategorySerializer(subcategory, data=request.data, partial=True)
        
        if serializer.is_valid():
            name = request.data.get("name")
            description = request.data.get("description")
            category_id = request.data.get("category")
            parent_id = request.data.get("parent")

            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                return Response({
                    "app_data": {
                        "StatusCode": 6002,
                        "data": {"message": "Category not found"}
                    }
                }, status=status.HTTP_404_NOT_FOUND)

            try:
                parent_subcategory = SubCategory.objects.get(id=parent_id)
            except SubCategory.DoesNotExist:
                return Response({
                    "app_data": {
                        "StatusCode": 6002,
                        "data": {"message": "Parent SubCategory not found"}
                    }
                }, status=status.HTTP_404_NOT_FOUND)

            subcategory.name = name
            subcategory.description = description
            subcategory.category = category
            subcategory.parent = parent_subcategory
            subcategory.save()

            response_data = {
                "StatusCode": 6000,
                "data": serializer.data,
                "message": "Subcategory updated successfully"
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": generate_serializer_errors(serializer.errors)
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
        response_data = {
            "StatusCode":  6000,
            "data" : {
                "message" : f"{subcategory.name} deleted Successfully"
            }
        }
    except SubCategory.DoesNotExist:
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


