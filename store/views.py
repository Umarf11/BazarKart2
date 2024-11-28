from django.shortcuts import render, get_object_or_404
from store.models import Product
from category.models import Category
from django.core.paginator import Paginator
from carts.models import CartItem
from carts.views import _cart_id

# Create your views here.


def store(request, category_slug=None):
    categories = None
    products = None
    if category_slug is not None:
        categories = get_object_or_404(Category, slug=category_slug)
        categorys = Category.objects.all().order_by('id')
        products = Product.objects.filter(category=categories).order_by('id')
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().order_by('id')
        categorys = Category.objects.all().order_by('id')
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    context = {
        'products': paged_products,
        'product_count': product_count,
        'categorys': categorys
    }
    return render(request, 'store.html', context)


def product_details(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e
    context = {
        'single_product': single_product,
        'in_cart': in_cart,

    }
    return render(request, 'product_details.html', context)


def search(request):
    products = Product.objects.none()  # Default to an empty QuerySet
    product_count = 0  # Default to 0

    if 'keyword' in request.GET:
        keyword = request.GET['keyword'].strip()  # Strip any unnecessary whitespace
        if keyword:
            products = Product.objects.filter(product_name__icontains=keyword)
            product_count = products.count()

    context = {
        'products': products,
        'product_count': product_count,
    }
    return render(request, 'store.html', context)

