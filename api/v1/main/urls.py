from django.urls import path, re_path
from .views import FileUploadView
app_name = "api_v1_main"

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
]