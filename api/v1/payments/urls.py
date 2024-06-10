from django.urls import path, re_path
from . import views

app_name = "api_v1_payments"


urlpatterns = [
    # re_path(r'^proceed-payment/$', views.create_checkout_session, name="checkout"),
    # re_path(r'^payment-success/$', views.payment_success, name="checkout"),
    re_path(r'^create-order/$', views.create_order, name="create_order"),
    re_path(r'^handle-response/$', views.handle_response, name="create_order")
]