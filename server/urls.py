from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/main/', include('api.v1.main.urls', namespace='api_v1_main')),

    path('api/v1/accounts/', include('api.v1.accounts.urls', namespace='api_v1_accounts')),
    path('api/v1/products/', include('api.v1.products.urls', namespace='api_v1_products')),
    path('api/v1/marketing/', include('api.v1.marketing.urls', namespace='api_v1_marketing')),
    path('api/v1/activities/', include('api.v1.activities.urls', namespace='api_v1_activities')),
]
