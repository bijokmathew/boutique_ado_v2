from django.http import HttpResponse


class StripeWH_handler:
    """
    Handle stripe webhooks
    """
    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        """
        Handle generic/unknown/unexpected webhook
        events
        """
        return HttpResponse(
           content=f'Webhook recieved: {event["type"]} ',
           status=200
        )
