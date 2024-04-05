from django.urls import path, re_path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

app_name = "api_v1_accounts"
urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    re_path(r"^signup/$", views.signup, name="signup"),
    re_path(r"^change-password/$", views.change_password, name="change_password"),
    re_path(r"^verify/$", views.verify, name="verify"),
    re_path(r"^login/$", views.login, name="login"),
    re_path(r"^add_address/$", views.add_address, name="add_address"),
    re_path(r"^view_addresses/$", views.view_addresses, name="view_addresses"),
    re_path(
        r"^change_primary_address/(?P<address_id>.*)/$",
        views.change_primary_address,
        name="change_primary_address",
    ),
    re_path(
        r"^edit_address/(?P<address_id>.*)/$", views.edit_address, name="edit_addresss"
    ),
    re_path(
        r"^delete_address/(?P<address_id>.*)/$",
        views.delete_address,
        name="delete_address",
    ),
    re_path(r"^viewstaff/$", views.viewstaff, name="viewstaff"),
    re_path(r"^view-user/$", views.view_user, name="view_user"),
    # -------------admin---------------------
    re_path(r"^admin/signup/$", views.adminSignup, name="admin_signup"),
    re_path(r"^admin/account-details/$", views.accountDetails, name="account_details"),
    re_path(r"^admin/edit-account/$", views.edit_account, name="edit_account"),
    re_path(r"^admin/login/$", views.admin_login, name="admin_login"),
    re_path(r"^admin/add-staff/$", views.addStaff, name="add-staff"),
    re_path(r"^admin/edit-staff/(?P<pk>.*)/$", views.edit_staff, name="edit-staff"),
    re_path(
        r"^admin/delete-staff/(?P<pk>.*)/$", views.delete_staff, name="delete-staff"
    ),
    re_path(r"^admin/change-password/$", views.change_password, name="change_password"),
    re_path(r"^admin/costomers/$", views.costemers, name="admin_costomers"),
]
