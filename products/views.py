from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from django.db.models import Q
from .models import Product, Category


def all_products(request):
    """
        A view to show all products, including sorting and search queries
    """
    products = Product.objects.all()
    query = None
    category_list = None
    if request.GET:
        if 'category' in request.GET:
            category_list = request.GET['category'].split(',')
            products = Product.objects.filter(category__name__in=category_list)
            category_list = Category.objects.filter(name__in=category_list)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria !!")
                return redirect(reverse('products'))
            else:
                queries = Q(name__icontains=query) | Q(description__icontains=query)
                products = Product.objects.filter(queries)

    context = {
        'products': products,
        'current_category': category_list,
    }
    return render(request, "products/products.html", context)


def product_detail(request, product_id):
    """
        A view to show indivijual product detail
    """
    product = get_object_or_404(Product, pk=product_id)
    context = {
        'product': product,
    }
    return render(request, "products/product_detail.html", context)