from django.urls import path, re_path
from . import views


app_name = "api_v1_products"


urlpatterns = [
    # -----------------public------------
    re_path(r"^category/$", views.categories, name="categories"),
    re_path(r"^brands/$", views.brands, name="brands"),
    re_path(r"^viewproduct/$", views.viewProduct, name="viewProduct"),
    re_path(
        r"^viewproduct/(?P<pk>.*)/$", views.viewProductSingle, name="viewProductSingle"
    ),
    re_path(
        r"^sub-category/(?P<pk>.*)/$", views.viewSubCategory, name="sub-categories"
    ),
    re_path(
        r"^view-sub-category/(?P<type>.*)/$",
        views.viewSubCategory,
        name="sub-categories",
    ),
    re_path(
        r"^view-sub-category-item/(?P<pk>.*)/$",
        views.viewSubCategoryItem,
        name="sub-categories_item",
    ),
    re_path(
        r"^edit-sub-category-item/(?P<pk>.*)/$",
        views.editSubCategoryItem,
        name="edit_sub-categories",
    ),
    re_path(
        r"^edit-categoryposition/(?P<pk>.*)/$",
        views.editCategoryPosition,
        name="editCategoryPosition",
    ),
    re_path(
        r"^edit-subcategoryposition/(?P<pk>.*)/$",
        views.editSubCategoryPosition,
        name="editCategoryPosition",
    ),
    re_path(
        r"^filter_products_by_price/$",
        views.product_list_by_price_range,
        name="product_list_by_price_range",
    ),
    re_path(r"^new_arrivals/$", views.new_arrivals, name="new_arrivals"),
    re_path(r"^view_attribute/$", views.view_attribute, name="view_attribute"),
    re_path(
        r"^get-related-product/$", views.get_related_product, name="get_related_product"
    ),
    re_path(r"^get-category-tree/$", views.get_category_tree, name="get_category_tree"),
    # ---------------admin-------------
    re_path(r"^admin/add-attribute/$", views.add_new_attribute, name="add_attribute"),
    re_path(r"^admin/product/$", views.admin_product, name="admin_product"),
    re_path(r"^admin/addCategory/$", views.addCategory, name="add_category"),
    re_path(r"^admin/addBrand/$", views.addBrand, name="add_brand"),
    re_path(r"^admin/viewBrands/$", views.brands, name="view_Brands"),
    re_path(r"^admin/editBrands/(?P<pk>.*)/$", views.editBrand, name="view_Brands"),
    re_path(
        r"^admin/deleteBrand/(?P<pk>.*)/$", views.deleteBrand, name="delete_Brands"
    ),
    re_path(r"^admin/addAttribute/$", views.addAttribute, name="add_attribute"),
    re_path(r"^admin/listAttributes/$", views.listAttributes, name="list_attributes"),
    re_path(
        r"^admin/editAttribute/(?P<pk>.*)/$", views.editAttribute, name="edit_Attribute"
    ),
    re_path(
        r"^admin/deleteAttribute/(?P<pk>.*)/$",
        views.deleteAttribute,
        name="delete_Attribute",
    ),
    re_path(r"^view-attribute-type/$", views.viewAttributeType, name="view_Attribute"),
    re_path(
        r"^view-attribute-description/(?P<pk>.*)/$",
        views.viewAttributeDescription,
        name="view_Attribute",
    ),
    re_path(r"^admin/addProduct/$", views.addProductNew, name="add_product"),
    re_path(r"^view-productcode/$", views.viewProductCode, name="view_productcode"),
    re_path(r"^get-varients/$", views.get_varients, name="get_varients"),
    # re_path(r'^admin/addProduct/$', views.addProduct, name="add_product"),
    re_path(r"^admin/addVarient/(?P<pk>.*)/$", views.addVarient, name="add_varient"),
    re_path(
        r"^admin/add-product-varient/(?P<pk>.*)/$",
        views.addProductVarient,
        name="add_product_varient",
    ),
    re_path(r"^admin/add-subcategory/$", views.addSubcategory, name="add_subcategory"),
    re_path(
        r"^admin/view-subcategory/(?P<pk>.*)/$",
        views.viewSubCategory,
        name="view_subcategory",
    ),
    re_path(
        r"^admin/view-products/(?P<pk>.*)/$",
        views.view_admin_single_product,
        name="view_subcategory",
    ),
    re_path(
        r"^admin/delete-products/(?P<pk>.*)/$",
        views.delete_product,
        name="delete_product",
    ),
    re_path(
        r"^admin/add-to-featured/(?P<pk>.*)/$",
        views.add_to_featured,
        name="add_to_featured",
    ),
    re_path(
        r"^admin/add-to-flashsale/(?P<pk>.*)/$",
        views.add_to_flashsale,
        name="add_to_featured",
    ),
    re_path(
        r"^view-subcategory/(?P<pk>.*)/$",
        views.subcategory_tree,
        name="view_subcategory_tree",
    ),
    re_path(r"^view-category/$", views.category_tree, name="category_tree"),
    re_path(
        r"^admin/add-product-items/(?P<pk>.*)/$",
        views.addProductItem,
        name="addProductItem",
    ),
    re_path(
        r"^admin/edit-category/(?P<pk>.*)/$", views.editCategory, name="editCategory"
    ),
    re_path(
        r"^admin/delete-category/(?P<pk>.*)/$",
        views.deleteCategory,
        name="deleteCategory",
    ),
    re_path(
        r"^admin/edit-subcategory/(?P<pk>.*)/$",
        views.editSubCategory,
        name="editCategory",
    ),
    re_path(
        r"^admin/delete-subcategory/(?P<pk>.*)/$",
        views.deleteSubCategory,
        name="deleteCategory",
    ),
    re_path(
        r"^admin/product-single/(?P<pk>.*)/$", views.productSingle, name="productSingle"
    ),
    re_path(r"^admin/inventory/$", views.inventory, name="inventory"),
    re_path(r"^admin/view-stock/(?P<pk>.*)/$", views.view_stock, name="inventory"),
    re_path(r"^admin/update-quantity/$", views.update_quantity, name="update_quantity"),
    re_path(
        r"^admin/attribute/(?P<pk>.*)/$",
        views.attribute_detail,
        name="attribute_detail",
    ),
    re_path(
        r"^admin/edit-attribute/$",
        views.edit_attribute,
        name="attribute_detail",
    ),
    re_path(
        r"^admin/update-publish/(?P<pk>.*)/$",
        views.update_publish,
        name="update_publish",
    ),
]
