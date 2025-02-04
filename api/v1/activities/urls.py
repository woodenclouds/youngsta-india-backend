from django.urls import path, re_path
from . import views

app_name = "api_v1_activities"


urlpatterns = [
    # -----------------public------------
    re_path(
        r"^add_to_wishlist/(?P<pk>.*)/$", views.add_to_wishlist, name="add_to_wishlist"
    ),
    re_path(r"^view_wishlist/$", views.view_wishlist, name="view_wishlist"),
    re_path(
        r"^edit_wishlist_item/(?P<pk>.*)/$",
        views.edit_wishlist_item,
        name="edit_wishlist_item",
    ),
    re_path(
        r"^delete_wishlist_item/(?P<pk>.*)/$",
        views.delete_wishlist_item,
        name=" delete_wishlist_item",
    ),
    # re_path(r'^get-refferal-link/(?P<pk>.*)/$', views.get_refferal_link, name="get_refferal_link"),
    re_path(r"^add_to_cart/(?P<pk>.*)/$", views.add_to_cart, name="add_to_cart"),
    re_path(r"^add-refferal/$", views.add_referral, name="add_refferal"),
    re_path(r"^apply-coupen/$", views.apply_coupen, name="apply_coupen"),
    re_path(r"^apply-wallet-amount/$", views.apply_wallet_amount, name="apply_wallet_amount"),
    re_path(
        r"^remove_from_cart/(?P<pk>.*)/$",
        views.remove_from_cart,
        name="remove_from_cart",
    ),
    re_path(
        r"^edit_cart_item/(?P<pk>.*)/$", views.edit_cart_item, name="edit_cart_item"
    ),
    
    # track shipment 
    re_path(r"^orders/track/(?P<shipment_id>.*)/$", views.track_order_by_shipment_id, name="track_order_by_shipment_id"),
    
    
    re_path(r"^view_cart_items/$", views.get_cart, name="view_cart_items"),
    re_path(r"^orders/$", views.orders, name="orders"),
    re_path(r"^orders-details/(?P<pk>.*)/$", views.orders_details, name="orders"),
    re_path(r"^purchase_items/$", views.purchase_items, name="purchase_items"),
    re_path(r"^return_items/(?P<pk>.*)/$", views.return_items, name="purchase_items"),
    re_path(r"^cancel_items/(?P<pk>.*)/$", views.cancel_items, name="purchase_items"),
    re_path(
        r"^create-refferal/(?P<pk>.*)/$", views.create_refferal, name="create_refferal"
    ),
    re_path(r"^admin-refferals/$", views.admin_referals, name="admin_referals"),
    re_path(r"^viewPurchase/$", views.viewPurchase, name="viewPurchase"),
    re_path(r"^success/(?P<pk>.*)/$", views.purchase_success, name="purchase_success"),
    re_path(r"^failure/(?P<pk>.*)/$", views.purchase_failure, name="purchase_success"),
    re_path(r"^admin/accounts/$", views.accounts_details, name="accounts_details"),
    re_path(r"^wallet/$", views.wallet, name="wallet"),
    re_path(
        r"^update-all-refferal/$", views.update_all_refferal, name="update_all_refferal"
    ),
    re_path(r"^admin/best-selling-product/$", views.best_selling_product, name="best_selling_product"),
    re_path(r"^user-orders/$", views.user_orders, name="user-orders"),
    re_path(r"^admin/orders/$", views.view_oders, name="view_oders"),
    re_path(r"^admin/orders/(?P<pk>.*)/$", views.view_oder_detail, name="view_oders"),
    re_path(r"^admin/transactions/$", views.view_accounts, name="view_accounts"),
    re_path(r"^admin/purchase-graph/$", views.total_sales, name="total_sales"),
    re_path(r"^admin/dashboard-data/$", views.order_stats, name="view_purchases"),
    re_path(r"^admin/product-count/$", views.product_count, name="product_count"),
    re_path(r"^admin/view-status/$", views.view_statusses, name="view_statusses"),
    re_path(r"^admin/get-service-availability/$", views.get_service_availability, name="view_statusses"),

    re_path(
        r"^admin/add-purchase-log/(?P<pk>.*)/$",
        views.add_purchase_log,
        name="add_purchase_log",
    ),
    re_path(
        r"^admin/view-order-counts/$", views.view_order_count, name="view_order_count"
    ),

    re_path(r"^sources-list/$", views.order_source_list, name="order-sources-list"),
    re_path(r"^admin-create-orders/$", views.admin_create_orders, name="admin-create-orders"),
    re_path(r'^download-invoice/(?P<pk>.*)/$', views.download_invoice, name="download-invoice"),
    
    # financial years
    re_path(r"^admin/financial-year/$", views.get_financial_years, name="get-financial-year"),
    re_path(r"^admin/financial-year/create/$", views.create_financial_year, name="create-financial-year"),
    re_path(r"^admin/financial-year/(?P<pk>.*)/delete/$", views.delete_financial_year_status, name="delete-financial-year"),
    re_path(r"^admin/financial-year/(?P<pk>.*)/change-status/$", views.update_financial_year_status, name="update-financial-year-status"),

    # credit note
    re_path(r"^admin/credit-notes/$", views.get_credit_notes, name="get-credit-notes"),
    re_path(r"^admin/credit-notes/create/$", views.create_credit_note, name="create-credit-note"),
    re_path(r"^admin/credit-notes/(?P<pk>.*)/download/$", views.download_credit_note, name="download-credit-note"),
    
]
