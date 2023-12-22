from django.urls import path, re_path
from . import views

app_name = "api_v1_activities"



urlpatterns = [
    # -----------------public------------
    re_path(r'^add_to_wishlist/(?P<pk>.*)/$', views.add_to_wishlist, name="add_to_wishlist"),
    re_path(r'^view_wishlist/$', views.view_wishlist, name="view_wishlist"),
    re_path(r'^edit_wishlist_item/(?P<pk>.*)/$', views.edit_wishlist_item, name="edit_wishlist_item"),
    re_path(r'^delete_wishlist_item/(?P<pk>.*)/$', views. delete_wishlist_item, name=" delete_wishlist_item"),
   
 
   

  


]