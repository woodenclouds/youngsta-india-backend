from django.urls import path, re_path
from . import views

app_name = "api_v1_marketing"


urlpatterns = [
    # -----------------public------------
    # ---------------admin-------------
    re_path(
        r"^admin/add_advertisement/$", views.add_advertisement, name="add_advertisement"
    ),
    re_path(
        r"^admin/view_advertisement/$",
        views.view_advertisement,
        name="view_advertisement",
    ),
    re_path(r"^admin/edit_ads/(?P<pk>.*)/$", views.edit_ads, name="edit_advertisement"),
    re_path(
        r"^admin/delete_ads/(?P<pk>.*)/$", views.delete_ads, name="delete_advertisement"
    ),
    re_path(r"^admin/add_aditem/$", views.add_aditem, name="add_aditem"),
    re_path(r"^admin/edit_aditem/(?P<pk>.*)/$", views.edit_aditem, name="edit_aditem"),
    re_path(
        r"^admin/delete_aditem/(?P<pk>.*)/$", views.delete_aditem, name="delete_aditem"
    ),
    re_path(r"^admin/add-coupen/$", views.add_coupen, name="add_coupen"),
    re_path(r"^admin/edit-coupen/(?P<pk>.*)/$", views.editCoupen, name="add_coupen"),
    re_path(
        r"^admin/delete-coupen/(?P<pk>.*)/$", views.deleteCoupen, name="delete_coupen"
    ),
    re_path(r"^admin/get-coupen/$", views.get_coupens, name="add_coupen"),
    re_path(r"^admin/add-banner/$", views.add_banner, name="add_banner"),
    re_path(r"^admin/view-banners/$", views.view_banners, name="view_banner"),
    re_path(r"^admin/view-banners/(?P<pk>.*)/$", views.view_banner, name="view_banner"),
    re_path(r"^view-banners/(?P<section>.*)/$", views.view_user_banner, name="view_banner"),
    re_path(r"^admin/update-banners/(?P<pk>.*)/$", views.update_banner, name="view_banner"),
    re_path(r"^enquiry/$", views.enquiry, name="enquiry"),
    re_path(r"^admin/enquiry/$", views.admin_enquiry, name="admin_enquiry"),
]
