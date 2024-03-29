from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product


def bag_contents(request):
    bag_items = []
    total = 0
    product_count = 0
    bag = request.session.get('bag', {})
    for item_id, item_data in bag.items():
        product = get_object_or_404(Product, pk=item_id)
        if isinstance(item_data, int):
            total += product.price * item_data
            product_count += item_data
            bag_items.append({
                'item_id': item_id,
                'product': product,
                'quantity': item_data
            })
        else:
            for size, quantity in item_data['items_by_size'].items():
                total += product.price * quantity
                product_count += quantity
                bag_items.append({
                    'item_id': item_id,
                    'product': product,
                    'quantity': quantity,
                    'size': size
                 })

    if total < settings.FREE_DELIVERY_THRESHOLD:
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE)
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    else:
        delivery = 0
        free_delivery_delta = 0
 
    grand_total = total + delivery
    context = {
        'bag_items': bag_items,
        'total': total,
        'delivery': delivery,
        'product_count': product_count,
        'free_delivery_delta': free_delivery_delta,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
        'grand_total': grand_total,
    }

    return context