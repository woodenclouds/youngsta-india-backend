# views.py

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import FileSerializer 
from rest_framework.permissions import AllowAny
import boto3
from products.models import *

class FileUploadView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = FileSerializer(data=request.data)
        if serializer.is_valid():
            file_obj = serializer.validated_data['file']

            # Upload file to S3
            try:
                file_obj_name = file_obj.name
                s3 = boto3.client('s3')
                s3.upload_fileobj(file_obj, settings.AWS_STORAGE_BUCKET_NAME, file_obj_name)

                # Optionally, you can get the S3 URL for the uploaded file
                s3_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{file_obj_name}"

                product_gallery_entry = ProductGallery.objects.create(
                    image_name=file_obj_name,
                    image_url=s3_url
                )
                print("Product gallery entry",file_obj_name,s3_url)

                # Return the S3 URL or any other data as needed
                return Response({'url': s3_url}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
