from django.shortcuts import render, redirect


def view_bag(request):
    """
        A view that render the bag contents page
    """
    return render(request, "bag/bag.html")


def add_to_bag(request, item_id):
    """
    Add a quantity of the specified item to the shopping bag
    """
    quantity = int(request.POST.get('quantity'))
    redirect_url = request.POST.get('redirect-url')
    bag = request.session.get('bag', {})
    size = None
    if 'product_size' in request.POST:
        size = request.POST.get('product_size')

    if size:
        if item_id in list(bag.keys()):
            if size in bag[item_id]['items_by_size']:
                bag[item_id]['items_by_size'][size] += quantity
            else:
                bag[item_id]['items_by_size'][size] = quantity
        else:
            bag[item_id] = {'items_by_size': {size: quantity}}

    else:
        if item_id in list(bag.keys()):
            bag[item_id] += quantity
        else:
            bag[item_id] = quantity

    request.session['bag'] = bag
    print("bag =", request.session['bag'])
    return redirect(redirect_url)
