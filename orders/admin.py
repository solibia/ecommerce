# Register your models here.
from django.contrib import admin

from .models import Order, ProductPurchase

admin.site.register(Order)

admin.site.register(ProductPurchase)