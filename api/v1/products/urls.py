from django.urls import path, re_path
from . import views

app_name = "api_v1_products"



urlpatterns = [
    # -----------------public------------
   
    re_path(r'^category/$', views.categories, name="categories"),
    re_path(r'^brands/$', views.brands, name="brands"),
    re_path(r'^sub-category/$', views.viewSubCategory, name="sub-categories"),
    re_path(r'^edit-categoryorder/(?P<pk>.*)/$', views.editCategoryOrder, name="deleteCategory"),
   

    # ---------------admin-------------
    re_path(r'^admin/product/$', views.admin_product, name="admin_product"),
    re_path(r'^admin/addCategory/$', views.addCategory, name="add_category"),
    re_path(r'^admin/addBrand/$', views.addBrand, name="add_brand"),
    re_path(r'^admin/viewBrands/$', views.brands, name="view_Brands"),
    re_path(r'^admin/editBrands/(?P<pk>.*)/$', views.editBrand, name="view_Brands"),
    re_path(r'^admin/deleteBrand/(?P<pk>.*)/$', views.deleteBrand, name="delete_Brands"),
    re_path(r'^admin/addAttribute/$', views.addAttribute, name="add_attribute"),
    re_path(r'^admin/listAttributes/$', views.listAttributes, name="list_attributes"),
    re_path(r'^admin/editAttribute/(?P<pk>.*)/$', views.editAttribute, name="edit_Attribute"),
    re_path(r'^admin/deleteAttribute/(?P<pk>.*)/$', views.deleteAttribute, name="delete_Attribute"),
    re_path(r'^admin/addProduct/$', views.addProduct, name="add_product"),
    re_path(r'^admin/add-subcategory/$', views.addSubcategory, name="add_subcategory"),
    re_path(r'^admin/add-product-items/(?P<pk>.*)/$', views.addProductItem, name="addProductItem"),
    re_path(r'^admin/edit-category/(?P<pk>.*)/$', views.editCategory, name="editCategory"),
    re_path(r'^admin/delete-category/(?P<pk>.*)/$', views.deleteCategory, name="deleteCategory"),
    re_path(r'^admin/edit-subcategory/(?P<pk>.*)/$', views.editSubCategory, name="editCategory"),
    re_path(r'^admin/delete-subcategory/(?P<pk>.*)/$', views.deleteSubCategory, name="deleteCategory"),
    
]