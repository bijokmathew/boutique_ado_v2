from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.db.models.functions import Lower
from .models import Product, Category
from .forms import ProductForm


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


@login_required
def add_product(request):
    """
    Add products to the store
    """
    if not request.user.is_superuser:
        messages.error(request, f"Sorry!, only store owner can do that.")
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, "Successfully added product!")
            return redirect(reverse('product_detail', args=[product.id,]))
        else:
            messages.error(request, "Failed to add product. Please ensure the form is valid.")
    else:
        form = ProductForm()
    template = 'products/add_product.html'
    context = {
        'form': form
    }
    return render(request, template, context=context)


@login_required
def edit_product(request, product_id):
    """
    Edit product in the store
    """
    if not request.user.is_superuser:
        messages.error(request, f"Sorry!, only store owner can do that.")
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"Successfully updated the product")
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, f"Failed to update the product, Please ensure the form is valid")
    else:
        form = ProductForm(instance=product)
        messages.info(request, f"You are editing {product.name}")

    template = "products/edit_product.html"
    context = {
        'form': form,
        'product': product
    }

    return render(request, template, context=context)


@login_required
def delete_product(request, product_id):
    """
    Delete product from the store
    """
    if not request.user.is_superuser:
        messages.error(request, f"Sorry!, only store owner can do that.")
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, f"Product Deleted")
    return redirect(reverse('products'))
