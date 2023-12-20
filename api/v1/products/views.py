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
            category = Category.objects.create(
                name = name,
                description = description,
                image = image,
                cat_id=cat_id
            )
            transaction.commit()
            print(cat_id)
            response_data = {
                "StatusCode":6000,
                "data":{
                    "message":"category created succesfully"
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
        serialized = ViewCategorySerializer(
            instances,
            many=True
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

@api_view(["PUT", "PATCH"])
@group_required(["admin"])
def editCategory(request, pk):
    try:
        # Get the existing category instance
        category = Category.objects.get(id=pk)
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

@api_view(["DELETE"])
@group_required(["admin"])
def deleteCategory(request, pk):
    try:
        category = Category.objects.get(pk=pk)
        category.delete()
        response_data = {
            "StatusCode": 6000,
            "data" : {
                "message" : f"{category.name} deleted Successfully"
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


@api_view(["GET"])
@permission_classes((AllowAny,))
def brands(request):
    try:
        instance = Brand.objects.all()
        serialized = BrandSerializer(
            instance,
            many=True
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


@api_view(["POST"])
@group_required(["admin"])
def addSubcategory(request,pk):
    try:
        transaction.set_autocommit(False)
        serialized = AddSubCategorySerializer(data=request.data)
        error = False
        if not serialized.is_valid():
            error = True
            response_data = {
                    "StatusCode": 6001,
                    "data": generate_serializer_errors(serialized._errors)
                }
        if not Category.objects.filter(pk=pk).exists():
            error = True
            response_data = {
                "StatusCode":6001,
                "data":{
                    "message":"category not exist"
                }
            }
        if not error:
            name = request.data["name"]
            description = request.data["description"]
            category = Category.objects.get(pk=pk)
            if not SubCategory.objects.filter(name=name,category=category).exists():
                sub_category = SubCategory.objects.create(
                    name = name,
                    description = description,
                    category = category
                )
                transaction.commit()
                response_data={
                    "StatusCode":6000,
                    "data":{
                        "message":f"{sub_category.name} successfully created"
                    }
                }
            else:
                response_data = {
                    "StatusCode":6001,
                    "data":{
                        "message":"subcategory already exists"
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