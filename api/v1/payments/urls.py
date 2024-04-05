from django.urls import path, re_path
from . import views

app_name = "api_v1_payments"


urlpatterns = [
    # re_path(r'^proceed-payment/$', views.create_checkout_session, name="checkout"),
    # re_path(r'^payment-success/$', views.payment_success, name="checkout")
]