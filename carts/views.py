from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
import stripe
from django.conf import settings
from django.http import JsonResponse
# Create your views here.


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    try:
        # Ensure you're using `cart_id` here
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )
    cart.save()

    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart,
        )
        cart_item.save()

    return redirect('cart')


def cart(request, total=0, quantity=0, cart_item=None):
    try:
        tax = 0
        grand_total = 0
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        cart_items = []
    context = {
        'cart': cart,
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'cart.html', context)


def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(cart=cart, product=product)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:

        cart_item.delete()
    return redirect('cart')


def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(cart=cart, product=product)
    cart_item.delete()
    return redirect('cart')


stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(request, cart_id):
    # Get the cart using the cart_id
    cart = get_object_or_404(Cart, pk=cart_id)
    
    # Retrieve active cart items
    cart_items = CartItem.objects.filter(cart=cart, is_active=True)
    
    # Calculate the total amount (sum of all cart items)
    total_amount = sum(item.sub_total() for item in cart_items)

    # Optionally, log or check the total amount for debugging purposes
    print(f"Total amount (calculated): {total_amount} USD")

    # Create Stripe checkout session
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'pkr',
                    'product_data': {
                        'name': item.product.product_name,
                    },
                    'unit_amount': int(item.product.price * 100),  # Stripe expects amount in cents
                },
                'quantity': item.quantity,
            } for item in cart_items],
            mode='payment',
            success_url=request.build_absolute_uri('/cart/payment/success/'),
            cancel_url=request.build_absolute_uri('/cart/payment/cancel/'),
        )
        
        # Return a redirect to the Stripe checkout page
        return redirect(checkout_session.url)
    
    except Exception as e:
        # Catch errors and return an error message (optional)
        return render(request, 'error_page.html', {'error': str(e)})


def payment_success(request):
    return render(request, 'payment_success.html')


def payment_cancel(request):
    return render(request, 'payment_cancel.html')


def stripe_form(request, cart_id):
    cart = get_object_or_404(Cart, pk=cart_id)
    cart_items = CartItem.objects.filter(cart=cart, is_active=True)
    total = sum(item.sub_total() for item in cart_items)
    
    return render(request, 'stripe_form.html', {'cart': cart, 'cart_items': cart_items, 'total': total})
