from django.http import HttpResponse
from .models import Order, OrderLineItem
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
import json
import time
import stripe
from profiles.models import UserProfile
from products.models import Product


class StripeWH_handler:
    """
    Handle stripe webhooks
    """
    def __init__(self, request):
        self.request = request
    
    def _send_confirmation_email(self, order):
        """ Send the user confirmation email"""
        cust_email = order.email
        subject = render_to_string(
            'checkout/confirmation_emails/confirmation_email_subject.txt',
            {
                'order': order
            }
        )
        body = render_to_string(
            'checkout/confirmation_emails/confirmation_email_body.txt',
            {
                'order': order,
                'contact_email': settings.DEFAULT_FROM_EMAIL
            }
        )

        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [cust_email]
        )

    def handle_event(self, event):
        """
        Handle generic/unknown/unexpected webhook
        events
        """
        return HttpResponse(
           content=f'Unhandled webhook recieved: {event["type"]}',
           status=200
        )
   
    def handle_payment_intent_succeeded(self, event):
        """
        Handle payment_intent.succeeded webhook
        event from stripe
        """
        intent = event.data.object
        pid = intent.id
        bag = intent.metadata.bag
        save_info = intent.metadata.save_info
        # Get charge object
        stripe_charge = stripe.Charge.retrieve(
            intent.latest_charge
        )
        billing_details = stripe_charge.billing_details
        shipping_details = intent.shipping
        grand_total = round(stripe_charge.amount / 100, 2)

        # Clean data in the shipping details
        for field, value in shipping_details.address.items():
            if value == '':
                shipping_details.address[field] = None
        attempt = 1
        order_exits = False

        while attempt < 5:
            try:
                order = Order.objects.get(
                    full_name__iexact=shipping_details.name,
                    email__iexact=billing_details.email,
                    phone_number__iexact=shipping_details.phone,
                    country__iexact=shipping_details.address.country,
                    postcode__iexact=shipping_details.address.postal_code,
                    town_or_city__iexact=shipping_details.address.city,
                    street_address1__iexact=shipping_details.address.line1,
                    street_address2__iexact=shipping_details.address.line2,
                    county__iexact=shipping_details.address.state,
                    grand_total=grand_total,
                    stripe_pid=pid,
                    original_bag=bag
                )
                order_exits = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)
        if order_exits:
            self._send_confirmation_email(order)
            return HttpResponse(
                    content=f'Webhook succ recieved: {event["type"]} \
                        | Success: Verified order already in database',
                            status=200
                    )
        else:
            order = None
            try:
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    user_profile=profile,
                    email=billing_details.email,
                    phone_number=shipping_details.phone,
                    country=shipping_details.address.country,
                    postcode=shipping_details.address.postal_code,
                    town_or_city=shipping_details.address.city,
                    street_address1=shipping_details.address.line1,
                    street_address2=shipping_details.address.line2,
                    county=shipping_details.address.state,
                    grand_total=grand_total,
                    stripe_pid=pid,
                    original_bag=bag
                )
                for item_id, item_data in json.loads(bag).items():
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data
                        )
                        order_line_item.save()
                    else:
                        for size, quantity in item_data['items_by_size'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
                
            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(
                    content=f'Webhook recieved: {event["type"]} | ERROR: {e}',
                    status=500
                )
            # Updated the profile info if save_info was checked
            profile = None
            print("shipping_details.address.line1", shipping_details.address.line1)
            username = intent.metadata.username
            if username != 'AnonymousUser':
                profile = UserProfile.objects.get(user__username=username)
                if save_info:
                    profile.default_phone_number = shipping_details.phone,
                    profile.default_country = shipping_details.address.country,
                    profile.default_postcode = shipping_details.address.postal_code,
                    profile.default_town_or_city = shipping_details.address.city,
                    profile.default_street_address1 = shipping_details.address.line1,
                    profile.default_street_address2 = shipping_details.address.line2,
                    profile.default_county = shipping_details.address.state,
                    profile.save()
            self._send_confirmation_email(order)
        return HttpResponse(
           content=f'Webhook succ recieved: {event["type"]} | Success: created order in webhook ',
           status=200
        )

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle payment_intent.payment_failed webhook event
        from stripe
        """
        return HttpResponse(
           content=f'Webhook fail recieved: {event["type"]}',
           status=200
        )
