from django.db import models
from django.db.models import Sum
from django.conf import settings
from products.models import Product
import uuid


class Order(models.Model):
    """
    This model handle all orders in the website
    """
    order_number = models.CharField(max_length=32, blank=False, null=False, editable=False)
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    country = models.CharField(max_length=40, null=False, blank=False)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    street_address1 = models.CharField(max_length=80, null=False, blank=False)
    street_address2 = models.CharField(max_length=80, null=False, blank=False)
    county = models.CharField(max_length=40, null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    delivery_cost = models.DecimalField(max_digits=6, decimal_places=2, null=False,default=0)
    order_total = models.DecimalField(max_digits=10, decimal_places=2, null=False,default=0)
    grand_total = models.DecimalField(max_digits=6, decimal_places=2, null=False,default=0)

    def __generate_order_number(self):
        """
        Generate a random, unique order number using uuid
        """
        return uuid.uuid4().hex.upper()

    def update_total(self):
        """
        Update grand total by adding the inline_total 
        to the specific order
        """
        self.order_total = self.lineitems.aggregate(Sum('lineitem_total'))['lineitem_total__sum']
        if self.order_total < settings.FREE_DELIVERY_THRESHOLD:
            self.delivery_cost = self.order_total * settings.STANDARD_DELIVERY_PERCENTAGE/100
        else:
            self.delivery_cost = 0
        self.grand_total = self.order_total + self.delivery_cost
        self.save()

    def save(self, *args, **kwargs):
        """
        Override the original save method to set
        order number it it has not set already
        """
        if not slef.order_number():
            self.order_number = self.__generate_order_number()
        super().save(*args, **kwargs)
 
        def __str__(self):
            return self.order_number


class OrderLineItem(models.Model):
    """
    This model has all products related to specific order
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=False, blank=False, related_name='lineitems')
    product = models.ForeignKey(Order, on_delete=models.CASCADE, null=False, blank=False)
    quantity = models.IntegerField(null=False, blank=False, default=0)
    product_size = models.CharField(max_length=3, null=True, blank=False)
    linitem_total = models.DecimalField(max_digits=6, decimal_places=2, null=False, blank=False)

    def __str__(self):
        return f'SKU: {self.product.sku} on order {self.order.order_number}'

    def save(self, *args, **kwargs):
        """
        Override the original save method to set
        lineitem_total and update the order total
        """
        self.lineitem_total = self.product.price * self.quantity
        super().save(*arg, **kwargs)
