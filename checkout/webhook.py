from django.conf import settings
from django.http import HttpResponse
from checkout.webhook_handler import StripeWH_handler
import stripe
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt


@require_POST
@csrf_exempt
def webhook(request):
    """
    Listen for webhook from the stripe
    """
    print('--------------webhook----------')
    # setup
    wh_secret = 'whsec_4vFBzyvMq6hVIMwr1u71O4lZXObXChJy'  # settings.STRIPE_WH_SECRET
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Get the webhook data and verify its signature
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    print('sig_header', sig_header)
    print('wh_secret', wh_secret)
    print('stripe.api_key', stripe.api_key)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, wh_secret
         )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print("webhook inve->", e)
        # Invalid signature
        return HttpResponse(status=400)
    except Exception as e:
        return HttpResponse(content=e, status=400)

    # set up a webhook handler
    handler = StripeWH_handler(request)

    # Map webhook event to relevant handler function
    event_map = {
        'payment_intent.succeeded': handler.handle_payment_intent_succeeded,
        'payment_intent.payment_failed': handler.handle_payment_intent_payment_failed
    }

    # Get type of webhook event from stripe
    event_type = event['type']
    # If there is handler for it, get it from the event map
    # Use the generic one by default
    event_handler = event_map.get(event_type, handler.handle_event)

    # Call the event handler with the event
    response = event_handler(event)

    return response
