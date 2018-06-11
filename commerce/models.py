import uuid

from django.db import models
from django.conf import settings
from django.db.models import CharField, Model, ForeignKey, ManyToManyField, DateTimeField, DecimalField, IntegerField, ImageField, BooleanField
from account.models import Address, get_upload_image_path

# from itertools import count
# from crypto import Crypto
# from pycparser.ply.yacc import token

CATERGORIES = (('furniture','Furniture'), ('cad', 'CAD'))
CURRENCIES = (('usd','USD'), ('cad', 'CAD'), ('cny','CNY'))
STATUS = (('active','Active'), ('inactive', 'Inactive'))

class Category(Model):
    name = CharField(max_length=128, null=True, blank=True)
    description = CharField(max_length=500, null=True, blank=True)
#     status = CharField(max_length=16, choices=STATUS, default='active')
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

def get_restaurant_image_path(instance, fpath):
    import os
    fname, ext = os.path.splitext(fpath)
    return os.path.join('restaurants', str(instance.id) + ext)
    
class Restaurant(Model):
    name = CharField(max_length=255, null=True, blank=True)
    description = CharField(max_length=800, null=True, blank=True)
    address = ForeignKey(Address, null=True, blank=True, db_column='address_id', on_delete=models.CASCADE)
    categories = ManyToManyField(Category)
    image = ImageField(upload_to=get_restaurant_image_path)
    lat = DecimalField(max_digits=10, decimal_places=7, null=True)
    lng = DecimalField(max_digits=10, decimal_places=7, null=True)
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

# class Color(Model):
#     name = CharField(max_length=128, null=True, blank=True)
#     description = CharField(max_length=500, null=True, blank=True)
#     created = DateTimeField(auto_now_add=True)
#     updated = DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.name

class Style(Model):
    name = CharField(max_length=128, null=True, blank=True)
    description = CharField(max_length=500, null=True, blank=True)
    #status = CharField(max_length=16, choices=STATUS, default='active')
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class PriceRange(Model):
    low = DecimalField(max_digits=10, decimal_places=3, null=True)
    high = DecimalField(max_digits=10, decimal_places=3, null=True)
    step = DecimalField(max_digits=10, decimal_places=3, null=True)
    status = CharField(max_length=16, choices=STATUS, default='active')


class Product(Model):
    name = CharField(max_length=255, null=True, blank=True)
    description = CharField(max_length=1000, null=True, blank=True)
    status = CharField(max_length=16, choices=STATUS, default='active')
    fpath = CharField(max_length=512, null=True, blank=True)
    # dimension = CharField(max_length=64, null=True, blank=True)
    price = DecimalField(max_digits=10, decimal_places=3, null=True)
    currency = CharField(max_length=16, choices=CURRENCIES, default='usd')
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    #category = ForeignKey(Category, null=True, blank=True, db_column='category_id', on_delete=models.CASCADE)
    #style = ForeignKey(Style, null=True, blank=True, db_column='style_id', on_delete=models.CASCADE)
    #owner = ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, db_column='owner_id', on_delete=models.CASCADE)
    categories = ManyToManyField(Category)
    #color = ForeignKey(Color, null=True, blank=True, db_column='color_id', on_delete=models.CASCADE)
    restaurant = ForeignKey(Restaurant, null=True, blank=True, db_column='restaurant_id', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

def get_upload_image_path(instance, fpath):
    import os
    fname, ext = os.path.splitext(fpath)
    return os.path.join('products', str(instance.index) + ext)
    
class Picture(Model):
    name = CharField(max_length=256, null=True, blank=True)
    description = CharField(max_length=1024, null=True, blank=True)
    index = IntegerField(null=True)
    width = IntegerField(null=True)
    height = IntegerField(null=True)
    image = ImageField(upload_to=get_upload_image_path)
    product = ForeignKey(Product, null=True, blank=True, db_column='product_id', on_delete=models.CASCADE)
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Cart(Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now_add=True)


class CartItem(Model):
    quantity = IntegerField(null=True)
    product = ForeignKey(Product, null=True, blank=True, on_delete=models.CASCADE)
    cart = ForeignKey(Cart, null = True, blank=True, on_delete=models.CASCADE)
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now_add=True)


class Order(Model):
    user = ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    status = CharField(max_length=16, default='unpaid')
    currency = CharField(max_length=16, choices=CURRENCIES, default='cad')
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now_add=True)


class OrderItem(Model):
    order = ForeignKey(Order, null = True, blank=True, on_delete=models.CASCADE)
    product = ForeignKey(Product, null=True, blank=True, on_delete=models.CASCADE)
    quantity = IntegerField(null=True)
    

class FavoriteProduct(Model):
    user = ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, db_column='user_id', on_delete=models.CASCADE)
    ip = CharField(max_length=64, null=True, blank=True)
    product = ForeignKey(Product, null=True, blank=True, on_delete=models.CASCADE)
    status = BooleanField(default=False)
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)
