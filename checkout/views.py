from django.shortcuts import render, reverse, redirect
from django.contrib import messages
from .forms import OrderForm


def checkout(request):
    """
    This view render and return the checkout 
    template
    """
    bag = request.session.get('bag', {})
    if not bag:
        messages.error(request, "There is nothing in your bag at the momemt!")
        return redirect(reverse('products'))
    order_form = OrderForm()
    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': 'pk_test_51MnY04HYuD6x6xGkiGSdJWciyHvmodgWnGTqGewm2W4Y7dhvNGKqG1GrlI6VCaifVIaX28eWxpjndvgxxT1EDNKK00kR8Va1ln',
        'client_secret': 'test client secret'
    }   
    return render(request, template, context=context)
