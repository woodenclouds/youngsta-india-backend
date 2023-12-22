from django.urls import path, re_path
from . import views

app_name = "api_v1_marketing"


urlpatterns = [
    # -----------------public------------
   

   

    # ---------------admin-------------
 
    re_path(r'^admin/add_advertisement/$', views.add_advertisement, name="add_advertisement"),
    re_path(r'^admin/view_advertisement/$', views.view_advertisement, name="view_advertisement"),
    re_path(r'^admin/edit_ads/(?P<pk>.*)/$', views.edit_ads, name="edit_advertisement"),
    re_path(r'^admin/delete_ads/(?P<pk>.*)/$', views.delete_ads, name="delete_advertisement"),
    re_path(r'^admin/add_aditem/$', views.add_aditem, name="add_aditem"),
    re_path(r'^admin/edit_aditem/(?P<pk>.*)/$', views.edit_aditem, name="edit_aditem"),
    re_path(r'^admin/delete_aditem/(?P<pk>.*)/$', views.delete_aditem, name="delete_aditem"),

]               