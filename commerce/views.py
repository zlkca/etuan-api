import json
import os
import logging
from datetime import datetime
from django.db.models import Q,Count
from django.http import JsonResponse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from rest_framework_jwt.settings import api_settings
from django.core.exceptions import ObjectDoesNotExist#EmptyResultSet, MultipleObjectsReturned
from django.contrib.auth import get_user_model
from commerce.models import Restaurant, Picture, Product, Category, Order, OrderItem, Style, PriceRange, FavoriteProduct 
from account.models import Province, City, Address

from utils import to_json, obj_to_json, get_data_from_token

logger = logging.getLogger(__name__)

def processPictures(product, pictures):
    # pid --- product id
    # pictures --- dict that pass from the front end
    reindex = False
    pic = None
    for picture in pictures:            
        try:
            pic = Picture.objects.get(product_id=product.id, index=picture['index'])
        except:
            pic = None
        
        if pic:
            if picture['status'] == 'removed':
                reindex = True
                rmPicture(pic)
            elif picture['status'] == 'changed':
                savePicture(product, pic, picture)
                pic.save()
        else:# new
            pic = Picture()
            savePicture(product, pic, picture)
    
    if reindex:
        reindexPicture(product.id)
    
def savePicture(product, pic, picture):
    # product --- Product model object
    # pic --- Picture model object
    # picture --- dict from front end
    pic.index = picture['index']
    pic.name = picture['name']
    pic.product = product
    pic.image.save(picture['image'].name, picture['image'].file, True)
    pic.save()
                
def getDefaultPicture(pictures):
    if pictures.count() == 0:
        return ''
    else:
        if pictures.count()>0 and pictures[0].image.name:
            return pictures[0].image.name
        else:
            return ''

def rmPicture(pic):
    try:
        os.remove(pic.image.path)
    except:
        print('remove image failed')
    pic.image.delete()
    pic.delete()

def reindexPicture(pid):
    # pid --- product id
    pics = Picture.objects.filter(product_id=pid).order_by('index')
    i = 0
    for pic in pics:   
        pic.index = i
        i = i + 1
        pic.save()
        
def saveProduct(params):
    _id = params.get('id')
    if _id:
        item = Product.objects.get(id=_id)
    else:                    
        item = Product()

    item.name = params.get('name')
    item.description = params.get('description')
    item.price = params.get('price')
    item.currency = params.get('currency')
    
    restaurant_id = params.get('restaurant_id')
    try:
        item.restaurant = Restaurant.objects.get(id=restaurant_id)
    except:
        item.restaurant = None
        
    #item.category = category
    item.save()
#     item.categories.clear()
    # Assume there is only one image
#     n_pics = int(params.get('n_pictures'))
#             pictures = []
#             for i in range(n_pics):
#                 name = params.get('name%s'%i)
#                 status = params.get('image_status%s'%i)
#                 image = req.FILES.get('image%s'%i)
#                 pictures.append({'index':i,'name':name, 'status':status, 'image':image})
#                 
#             self.processPictures(item, pictures)
#             
#             # select default picture
#             pics = Picture.objects.filter(product_id=item.id)
#             item.fpath = self.getDefaultPicture(pics)
#             item.save()
    return item

def find_restaurants_by_location(lat, lng, distance):
    query = """SELECT *, 
        (
           3959 *
           acos(cos(radians(%s)) * 
           cos(radians(lat)) * 
           cos(radians(lng) - 
           radians(%s)) + 
           sin(radians(%s)) * 
           sin(radians(lat )))
        ) AS distance 
        FROM commerce_restaurant 
        HAVING distance < %s 
        ORDER BY distance LIMIT 0, 20;"""%(lat, lng, lat, distance)
    try:
        return Restaurant.objects.raw(query)
    except:
        return None
                
@method_decorator(csrf_exempt, name='dispatch')
class RestaurantView(View):
    def getList(self, req):
        lat = req.GET.get('lat')
        lng = req.GET.get('lng')
        distance = 25 # km
        restaurants = []
        admin_id = req.GET.get('admin_id')
        if admin_id: # need address
            try:
                item = Restaurant.objects.get(admin_id=admin_id)
                restaurant = to_json(item)
                restaurant['address'] = self.getAddress(item)
                return JsonResponse({'data':[restaurant]})
            except Exception:
                return JsonResponse({'data':[]})
        elif lat and lng: # do not need address
            restaurants = find_restaurants_by_location(lat, lng, distance)
        else:
            try:
                restaurants = Restaurant.objects.all()#.annotate(n_products=Count('product'))
            except Exception:
                return JsonResponse({'data':[]})
        rs =[]
        for r in restaurants:
            rs.append(to_json(r))
        
        return JsonResponse({'data': rs })
    
    def getAddress(self, restaurant):
        addr_id = restaurant.address.id
        item = None
        try:
            item = Address.objects.get(id=addr_id)
        except:
            item = None
        return to_json(item)
        
    def get(self, req, *args, **kwargs):
        pid = kwargs.get('id')
        if pid:
            try:
                item = Restaurant.objects.get(id=int(pid))
                p = obj_to_json(item, False)
                p['address'] = self.getAddress(item)
                return JsonResponse({'data':p})
            except Exception as e:
                print(e.message);
                return JsonResponse({'data':''})
        else: # get list
            return self.getList(req)#JsonResponse({'data':''})
        
    def delete(self, req, *args, **kwargs):
        pid = int(kwargs.get('id'))
        if pid:
            instance = Restaurant.objects.get(id=pid)
            instance.delete()
            items = Restaurant.objects.filter().order_by('-updated')
            return JsonResponse({'data':to_json(items)})
        return JsonResponse({'data':[]})
    
    def post(self, req, *args, **kwargs):
        params = req.POST
        authorizaion = req.META['HTTP_AUTHORIZATION']
        token = authorizaion.replace("Bearer ", "")
        data = get_data_from_token(token)
#         if data and data['username']=='admin':
        _id = params.get('id')
        if _id:
            item = Restaurant.objects.get(id=_id)
        else:                    
            item = Restaurant()
            
        item.name = params.get('name')
        item.description = params.get('description')
        item.lat = float(params.get('lat'))
        item.lng = float(params.get('lng'))
        item.created = item.created if item.created else datetime.now()
        addr_id = params.get('address_id')
        if(addr_id):
            addr = Address.objects.get(id=addr_id)
            self.saveAddress(addr, params)
            item.address = addr
        else:
            addr = Address()
            self.saveAddress(addr, params)
            item.address = addr
        item.save()
    
        image_status = params.get('image_status')
        if image_status == 'changed':
            self.rmPicture(item)
            image  = req.FILES.get("image")
            item.image.save(image.name, image.file, True)
            item.save()
        
        return JsonResponse({'data':to_json(item)})
    
    def saveAddress(self, addr1, params):
        addr1.street = params.get('street')
        addr1.sub_locality = params.get('sub_locality')
        addr1.postal_code = params.get('postal_code')
        addr1.lat = params.get('lat')
        addr1.lng = params.get('lng')
        addr1.province = params.get('province')
        addr1.city = params.get('city')
        addr1.save()
    
    def rmPicture(self, item):
        try:
            os.remove(item.image.path)
        except:
            print('remove image failed')
        item.image.delete()


@method_decorator(csrf_exempt, name='dispatch')
class CategoryView(View):
    def getList(self):
        categories = []
        try:
            categories = Category.objects.all()#.annotate(n_products=Count('product'))
        except Exception as e:
            logger.error('Get category Exception:%s'%e)
            return JsonResponse({'data':[]})
        return JsonResponse({'data': to_json(categories)})

    def get(self, req, *args, **kwargs):
        cid = kwargs.get('id')
        if cid:
            cid = int(cid)
            try:
                item = Category.objects.get(id=cid)
                return JsonResponse({'data':to_json(item)})
            except Exception as e:
                return JsonResponse({'data':''})
        else:
            return self.getList()
    
    def delete(self, req, *args, **kwargs):
        pid = int(kwargs.get('id'))
        if pid:
            instance = Category.objects.get(id=pid)
            instance.delete()
            items = Category.objects.filter().order_by('-updated')
            return JsonResponse({'data':to_json(items)})
        return JsonResponse({'data':[]})
    
    def post(self, req, *args, **kwargs):
        ubody = req.body.decode('utf-8')
        params = json.loads(ubody)

        _id = params.get('id')
        if _id:
            item = Category.objects.get(id=_id)
        else:                    
            item = Category()
            
        item.name = params.get('name')
        item.description = params.get('description')
#         item.status = params.get('status')
        item.save()
        return JsonResponse({'data':to_json(item)})

@method_decorator(csrf_exempt, name='dispatch')
class ProductListView(View):
    def get(self, req, *args, **kwargs):
        ''' get product list
        '''
        products = []
        cats = req.GET.get('cats')
        restaurants = req.GET.get('ms')
        colors = req.GET.get('colors')
        keyword = req.GET.get('keyword')
        kwargs = {}
        q = None
            
        if cats:
            q = Q(categories__id__in=cats.split(','))
        if restaurants:
            if q:
                q = q | Q(restaurant__id__in=restaurants.split(','))
            else:
                q = Q(restaurant__id__in=restaurants.split(','))
        if colors:
            if q:
                q = q | Q(color__id__in=colors.split(','))
            else:
                q = Q(restaurant__id__in=restaurants.split(','))

            
        restaurant_id = req.GET.get('restaurant_id')
        category_id = req.GET.get('category_id')
          
        if restaurant_id:
            products = Product.objects.filter(restaurant_id=restaurant_id).annotate(n_likes=Count('favoriteproduct'))
        elif category_id:
            products = Product.objects.filter(category_id=category_id).annotate(n_likes=Count('favoriteproduct'))
        elif cats or restaurants or colors:
            if keyword:
                products = Product.objects.filter(q).filter(Q(name__icontains=keyword)
                                                  |Q(categories__name__icontains=keyword)
                                                  |Q(restaurant__name__icontains=keyword)
                                                  |Q(color__name__icontains=keyword))
            else:
                products = Product.objects.filter(q)
        else:
            if keyword:
                products = Product.objects.filter(Q(name__icontains=keyword)
                                                  |Q(categories__name__icontains=keyword)
                                                  |Q(restaurant__name__icontains=keyword)
                                                  |Q(color__name__icontains=keyword))
            else:
                products = Product.objects.filter().annotate(n_likes=Count('favoriteproduct'))
                
        ps = to_json(products)
        for p in ps:
            try:
                pics = Picture.objects.filter(product_id=p['id'])
            except:
                pics = None
                 
            if pics:
                p['pictures'] = to_json(pics)

        #s = []
#         for product in products:
#             items = Item.objects.filter(product_id=product.id)
#             p = product.to_json()
#             p['n_likes'] = product.n_likes
#             p['n_items'] = len(items)
#             p['items'] = [items[0].to_json()]
#             fp = None
#             try:
#                 fp = FavoriteProduct.objects.get(user_id=uid)
#             except:
#                 pass
#                 
#             p['like'] = fp.status if fp else False

#             s.append(p)
        return JsonResponse({'data':ps})

    def post(self, req, *args, **kwargs):
        authorizaion = req.META['HTTP_AUTHORIZATION']
        token = authorizaion.replace("Bearer ", "")
        data = get_data_from_token(token)
        
        for key in req.POST:
            params = json.loads(req.POST[key])
            index = int(key.replace('info_', ''))
            product = saveProduct(params)
            image_status = params.get('image_status')
            if image_status == 'unchange':
                pass
            elif image_status == 'changed' or image_status == 'add':
                pictures = []
                image = req.FILES.get('image%s'%index)
                pictures.append({'index':0,'name':'', 'status':image_status, 'image':image})
                processPictures(product, pictures)
                
                # select default picture
                pics = Picture.objects.filter(product_id=product.id)
                product.fpath = getDefaultPicture(pics)
                product.save()
                
        return JsonResponse({'data':[]})
   
@method_decorator(csrf_exempt, name='dispatch')
class ProductFilterView(View):
    def get(self, req, *args, **kwargs):
        categories = Category.objects.all();
        styles = Style.objects.all();
        price_ranges = PriceRange.objects.all();
        return JsonResponse({'categories':categories, 'styles':styles, 'price_ranges':price_ranges})
    
@method_decorator(csrf_exempt, name='dispatch')
class ProductView(View):
    def get(self, req, *args, **kwargs):
        ''' get product detail with multiple items
        '''
        pid = int(kwargs.get('id'))
        if pid:
            try:
                products = Product.objects.filter(id=pid)
            except Exception as e:
                return JsonResponse({'product':''})
        else:
            return JsonResponse({'product':''})

        product = products[0]
        pics = Picture.objects.filter(product_id=product.id)
        ps = []
        for pic in pics:
            ps.append(to_json(pic))
 
        p = to_json(product)
        p['pictures'] = ps
        return JsonResponse({'data':p})
    
    def delete(self, req, *args, **kwargs):
        pid = int(kwargs.get('id'))
        if pid:
            instance = Product.objects.get(id=pid)
            instance.delete()
            items = Product.objects.filter().order_by('-updated')
            return JsonResponse({'data':to_json(items)})
        return JsonResponse({'data':[]})
    
    def post(self, req, *args, **kwargs):
        params = req.POST
        authorizaion = req.META['HTTP_AUTHORIZATION']
        token = authorizaion.replace("Bearer ", "")
        data = get_data_from_token(token)
        if data and data['username']=='admin' or data['utype']=='business':
            item = saveProduct(params)
            item.categories.clear()
            
            categories = params.get('categories').split(',')
            for cat_id in categories:
                try:
                    category = Category.objects.get(id=cat_id)
                except:
                    category = None
                item.categories.add(category)
            
            n_pics = int(params.get('n_pictures'))
            pictures = []
            for i in range(n_pics):
                name = params.get('name%s'%i)
                status = params.get('image_status%s'%i)
                image = req.FILES.get('image%s'%i)
                pictures.append({'index':i,'name':name, 'status':status, 'image':image})
                 
            processPictures(item, pictures)
             
            # select default picture
            pics = Picture.objects.filter(product_id=item.id)
            item.fpath = getDefaultPicture(pics)
            item.save()

            return JsonResponse({'tokenValid': True,'data':to_json(item)})
        return JsonResponse({'tokenValid':False, 'data':''})

            
@method_decorator(csrf_exempt, name='dispatch')
class OrderView(View):
    def getList(self, rid=None):
        orders = []
        try:
            if rid:
                orders = Order.objects.filter(restaurant_id=rid).order_by('created')
            else:
                orders = Order.objects.all().order_by('created')#.annotate(n_products=Count('product'))
            
            r = to_json(orders)
            for order in orders:
                items = OrderItem.objects.filter(order_id=order.id)
                ri = next((x for x in r if x['id'] == order.id), None)
                ri['items'] = to_json(items)
                ri['user']['username'] = order.user.username                    
        except Exception as e:
            logger.error('Get Order Exception:%s'%e)
            return JsonResponse({'data':[]})
        return JsonResponse({'data': r})

    def get(self, req, *args, **kwargs):
        cid = kwargs.get('id')
        if cid:
            cid = int(cid)
            try:
                item = Order.objects.get(id=cid)
                return JsonResponse({'data':to_json(item)})
            except Exception as e:
                return JsonResponse({'data':''})
        else:
            rid = req.GET.get('restaurant_id')
            return self.getList(rid)
        
    def post(self, req, *args, **kwargs):
        authorizaion = req.META['HTTP_AUTHORIZATION']
        token = authorizaion.replace("Bearer ", "")
        data = get_data_from_token(token)
        if data:
            uid = data['id']
            ubody = req.body.decode('utf-8')
            d = json.loads(ubody)
            # dict: {'orders': [{'restaurant_id': 2, 'items': [{'pid': 1, 'name': '土豆排骨', 'price': '12.000', 'restaurant_id': 
            #2, 'quantity': 4}, {'pid': 2, 'name': '泡椒豆腐', 'price': '12.000', 'restaurant_id': 2, 'quantity': 2}]}], 
            #'user_id': 7}
            orders = d.get("orders")
            for data in orders:
                rid = data['restaurant_id']
                items = data['items']
                order = Order()
                try:
                    restaurant = Restaurant.objects.get(id=rid)
                    user = get_user_model().objects.get(id=uid)
                    order.restaurant = restaurant
                    order.user = user
                    order.save()
                except Exception as e:
                    print(e)
                
                if order.id:
                    for item in items:
                        orderItem = OrderItem()
                        orderItem.order = order
                        orderItem.product = Product.objects.get(id=item['pid'])
                        orderItem.quantity = item['quantity']
                        orderItem.product_name = orderItem.product.name
                        orderItem.price = orderItem.product.price
                        orderItem.save()
                return JsonResponse({'success': True})
        return JsonResponse({'success':False})
    
@method_decorator(csrf_exempt, name='dispatch')
class FavoriteProductView(View):
    def get(self, req, *args, **kwargs):
        uid = req.GET.get('user_id')
        ps = Product.objects.annotate(n_likes=Count('favoriteproduct'))
        favorites = []
        for p in ps:
            product = p.to_json()
            product['n_likes'] = p.n_likes
            fp = None
            try:
                fp = FavoriteProduct.objects.get(user_id=uid)
            except:
                pass
                
            product['favorate'] = fp.status if fp else False
            favorites.append(product)
            
        return JsonResponse({'favorites':favorites})
    
    def post(self, req, *args, **kwargs):
        ubody = req.body.decode('utf-8')
        d = json.loads(ubody)
        uid = d.get("user_id")
        pid = d.get("product_id")
        try:
            like = FavoriteProduct.objects.get(user_id=uid, product_id=pid)
            like.delete()
        except ObjectDoesNotExist: 
            like = FavoriteProduct()
            like.product = Product.objects.get(id=pid)
            like.user = get_user_model().objects.get(id=uid)
            like.status = True
            like.save()   
        return JsonResponse({'success':'true'})    
        
