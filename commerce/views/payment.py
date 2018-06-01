import json
import logging
import stripe

from django.http import JsonResponse
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from commerce.models import Cart, CartItem
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from commerce.models import Picture, Product

logger = logging.getLogger(__name__)

# Set your secret key: remember to change this to your live secret key in production
# See your keys here: https://dashboard.stripe.com/account/apikeys
stripe.api_key = settings.STRIPE_API_KEY



@method_decorator(csrf_exempt, name='dispatch')
class PaymentView(View):

    def post(self, req, *args, **kwargs):
        ''' Add item to cart, create cart if not exist, only return the product just added
        '''
        params = json.loads(req.body)

        try:
            # Charge the user's card:
            o_charge = stripe.Charge.create(
    			source = params.get('stripeToken'),
    			amount = params.get('amount'),
    			currency = params.get('currency'),
    			description = params.get('description'),
    			metadata={"order_id": 6735}
    		)
        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            pass
        # buyer_id = params.get('buyer_id')
        # product_id = params.get('product_id')
        # cart = self.add_product_to_cart(buyer_id, product_id)
        # n = self.get_num_of_products(cart)

        return JsonResponse({'order_id':6735})
