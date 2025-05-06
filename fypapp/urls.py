from django.urls import path
from .views import *
from .views import add_to_cart, view_cart, remove_from_cart, add_to_wishlist, view_wishlist, remove_from_wishlist
from django.conf.urls.static import static
from fypapp import views
from . import views
from .debugging_cart import debug_cart_removal
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', ecommerce_view, name='ecommerce'),
    path('base/', base_view, name='base'),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),
    path('brand/', brand_view, name='brand'),
    path('get_price/', get_price, name='get_price'),
    path('Apple/', apple_view, name='Apple'),
    path('Dell/', dell_view, name='Dell'),
    path('hp/', hp_view, name='hp'),
    path('lenovo/', lenovo_view, name='lenovo'),
    path('microsoft/', microsoft_view, name='microsoft'),
    path('category/', category_list_view, name='category_list'),
    path("brands/", brand_list, name="brand_list"),
    path('search/', search, name='search'),
    
    path('product/<int:id>/', product_detail_view, name='product_detail'),
    path('trending/', views.trending_products_view, name='trending-products'),
    path('get_price/', views.get_price, name='get_price'),


    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),


    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
     path('cart/remove/<int:product_id>/<int:attribute_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Your new all-items remove endpoint (optional if you want to keep both)
    path('cart-count/', views.cart_count, name='cart_count'),
    path('cart/remove-all/<int:product_id>/<int:attribute_id>/', views.remove_all_from_cart, name='remove_all_from_cart'),
    path('cart/remove-all/<int:product_id>/<int:attribute_id>/', remove_all_from_cart, name='remove_all_from_cart'),
    path('debug/cart-remove/<int:product_id>/<int:attribute_id>/', debug_cart_removal, name='debug_cart_removal'),




    



    # --- Wishlist Views ---
    path('add-to-wishlist/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/', view_wishlist, name='view_wishlist'),
    path('wishlist-count/', wishlist_count, name='wishlist_count'),
    path("wishlist/remove/<int:wishlist_id>/", remove_from_wishlist, name="remove_from_wishlist"),
    path('wishlist/move-to-cart/<int:wishlist_id>/', move_to_cart, name='move_to_cart'),
    path('wishlist/move-all-to-cart/', views.move_all_to_cart, name='move_all_to_cart'),

    path('wishlist/move-to-cart/<int:wishlist_id>/', views.move_to_cart, name='move_to_cart'),
    path('wishlist/', views.wishlist_view, name='wishlist'),  # Ensure 'wishlist' URL exists


    # --- Checkout Views ---
    # path('checkout/', views.checkout_view, name='checkout'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('checkout/', views.checkout_view, name='checkout'),  # Add this line


    # --- CSRF Token ---
    path('get-csrf-token/', views.get_csrf_token, name='get_csrf_token'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
