import json
import logging

from django.http import JsonResponse
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from commerce.models import Cart, CartItem
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from commerce.models import Picture, Product

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class CartView(View):
    def get(self, req, *args, **kwargs):
        try:
            buyer_id = req.GET.get('buyer_id')
        except:
            buyer_id = None
        
        try:
            cart = Cart.objects.get(user_id=buyer_id)
            # find products for cart_product
            rs = self.get_items(cart)

            return JsonResponse({'cart':cart.to_json(), 'items':rs})

        except ObjectDoesNotExist:
            return JsonResponse({'cart':'', 'items':[]})

    def get_items(self, cart):
        rs = []
        cis = CartItem.objects.filter(cart_id=cart.id)
        for ci in cis:
            c = ci.to_json();
            
            items = Picture.objects.filter(product_id=ci.product.id)
            ps = []
            for item in items:
                ps.append(item.to_json())

            c['product']['items'] = ps
            rs.append(c)
        return rs

    def get_cart(self, buyer_id):
        cart = None
        try:
            cart = Cart.objects.get(user_id=buyer_id)
        except ObjectDoesNotExist:
            cart = Cart()
            cart.user = get_user_model().objects.get(id=buyer_id)
            cart.save()
        return cart

    def add_product_to_cart(self, buyer_id, product_id):
        cart = self.get_cart(buyer_id)        
        try:
            item = CartItem.objects.get(cart_id=cart.id, product_id=product_id)
            item.quantity += 1
            item.save()
        except ObjectDoesNotExist:
            item = CartItem()
            item.quantity = 1
            item.cart = cart
            try:
                product = Product.objects.get(id=product_id)
                item.product = product
                item.save()
            except Exception as e:
                logger.error("Exception Product doesn't exist: %s"%e)
        return cart

    def get_num_of_products(self, cart):
        items = CartItem.objects.filter(cart_id=cart.id)
        n = 0
        for item in items:
            n += item.quantity
        return n

    def post(self, req, *args, **kwargs):
        ''' Add item to cart, create cart if not exist, only return the product just added
        '''
        ubody = req.body.decode('utf-8')
        params = json.loads(ubody)
        buyer_id = params.get('buyer_id')
        product_id = params.get('product_id')
        cart = self.add_product_to_cart(buyer_id, product_id)
        n = self.get_num_of_products(cart)

        return JsonResponse({'nProducts':n})

    def delete(self, req, *args, **kwargs):
        ''' Delete products in the cart, if doesn't provide product_id means delete all
        '''
        buyer_id = req.GET.get('buyer_id')
        product_id = req.GET.get('product_id')
        cart = self.get_cart(buyer_id)

        if product_id:
            try:
                item = CartItem.objects.get(cart_id=cart.id, product_id=product_id)
                if item.quantity > 1:
                    item.quantity -= 1
                    item.save()
                else:
                    CartItem.objects.filter(cart_id=cart.id, product_id=product_id).delete()
            except ObjectDoesNotExist:
                pass
        else: # delete all
            CartItem.objects.filter(cart_id=cart.id).delete()
        
        items = self.get_items(cart)    
        n = self.get_num_of_products(cart)
        return JsonResponse({'nProducts':n, 'items':items})

