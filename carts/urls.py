from django.urls import path
from . import views


urlpatterns = [
    path('', views.cart, name="cart"),
    path('add_cart/<int:product_id>/', views.add_cart, name="add_cart"),
    path('remove_cart/<int:product_id>', views.remove_cart, name="remove_cart"),
    path('remove_cart_item/<int:product_id>', views.remove_cart_item, name="remove_cart_item"),
    path('cart/create_checkout_session/<int:cart_id>/', views.create_checkout_session, name='create_checkout_session'),
    
    # Payment success and cancel URLs
    path('cart/payment/success/', views.payment_success, name='payment_success'),
    path('cart/payment/cancel/', views.payment_cancel, name='payment_cancel'),
    
    # Stripe form URL where the user can view the cart and initiate the checkout process
    path('cart/stripe_form/<int:cart_id>/', views.stripe_form, name='stripe_form'),
]
