from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from django.db.models import Q
from django.db.models.functions import Lower
from .models import Product, Category


def all_products(request):
    """
        A view to show all products, including sorting and search queries
    """
    products = Product.objects.all()
    query = None
    category_list = None
    sort = None
    direction = None
    if request.GET:

        if 'category' in request.GET:
            category_list = request.GET['category'].split(',')
            products = Product.objects.filter(category__name__in=category_list)
            print("inside cat category_list= ", category_list)
            category_list = Category.objects.filter(name__in=category_list)

        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            print("sortkey =", sortkey)
            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))
                for product in products:
                    print("products", product.price)

            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
                print("sortkey f=", sortkey)
            products = products.order_by(sortkey)
            for product in products:
                print("products -last", product.price)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria !!")
                return redirect(reverse('products'))
            else:
                queries = Q(name__icontains=query) | Q(description__icontains=query)
                products = Product.objects.filter(queries)

    current_sorting = f'{sort}_{direction}'
    print("current_sorting =", current_sorting)
    print("current_category =", category_list)
    context = {
        'products': products,
        'current_category': category_list,
        'current_sorting': current_sorting,
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
