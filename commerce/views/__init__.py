import json
import os
import logging

from django.db.models import Q,Count
from django.http import JsonResponse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from rest_framework_jwt.settings import api_settings
from django.core.exceptions import ObjectDoesNotExist#EmptyResultSet, MultipleObjectsReturned
from django.contrib.auth import get_user_model
from commerce.models import Restaurant, Picture, Product, Category, Style, PriceRange, FavoriteProduct 
from utils import to_json, get_data_from_token

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class RestaurantView(View):
    def getList(self):
        restaurants = []
        try:
            restaurants = Restaurant.objects.all()#.annotate(n_products=Count('product'))
        except Exception as e:
            logger.error('Get manufactory Exception:%s'%e)
            return JsonResponse({'data':[]})
        return JsonResponse({'data': to_json(restaurants)})
    
    def get(self, req, *args, **kwargs):
        pid = kwargs.get('id')
        if pid:
            pid = int(pid)
            try:
                item = Restaurant.objects.get(id=pid)
                return JsonResponse({'data':to_json(item)})
            except Exception as e:
                print(e.message);
                return JsonResponse({'data':''})
        else: # get list
            return self.getList()#JsonResponse({'data':''})
        
    def delete(self, req, *args, **kwargs):
        pid = int(kwargs.get('id'))
        if pid:
            instance = Restaurant.objects.get(id=pid)
            instance.delete()
            items = Restaurant.objects.filter().order_by('-updated')
            return JsonResponse({'data':to_json(items)})
        return JsonResponse({'data':[]})
    
    def post(self, req, *args, **kwargs):
        params = json.loads(req.body)

        _id = params.get('id')
        if _id:
            item = Restaurant.objects.get(id=_id)
        else:                    
            item = Restaurant()
            
        item.name = params.get('name')
        item.description = params.get('description')
        item.save()
        return JsonResponse({'data':to_json(item)})



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
        params = json.loads(req.body)

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

# @method_decorator(csrf_exempt, name='dispatch')
# class ColorView(View):
#     def getList(self):
#         colors = []
#         try:
#             colors = Color.objects.all()#.annotate(n_products=Count('product'))
#         except Exception as e:
#             logger.error('Get Color Exception:%s'%e)
#             return JsonResponse({'data':[]})
#         return JsonResponse({'data': to_json(colors)})
    
#     def get(self, req, *args, **kwargs):
#         pid = kwargs.get('id')
#         if pid:
#             pid = int(pid)
#             try:
#                 item = Color.objects.get(id=pid)
#                 return JsonResponse({'data':to_json(item)})
#             except Exception as e:
#                 return JsonResponse({'data':''})
#         else:
#             return self.getList()
    
#     def delete(self, req, *args, **kwargs):
#         pid = int(kwargs.get('id'))
#         if pid:
#             instance = Color.objects.get(id=pid)
#             instance.delete()
#             items = Color.objects.filter().order_by('-updated')
#             return JsonResponse({'data':to_json(items)})
#         return JsonResponse({'data':[]})
    
#     def post(self, req, *args, **kwargs):
#         params = json.loads(req.body)

#         _id = params.get('id')
#         if _id:
#             item = Color.objects.get(id=_id)
#         else:                    
#             item = Color()
            
#         item.name = params.get('name')
#         item.description = params.get('description')
# #         item.status = params.get('status')
#         item.save()
#         return JsonResponse({'data':to_json(item)})

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
#             kwargs['categories__id__in'] = cats.split(',')
        if restaurants:
            if q:
                q = q | Q(manufactory__id__in=restaurants.split(','))
            else:
                q = Q(manufactory__id__in=restaurants.split(','))
#             kwargs['manufactory__id__in'] = restaurants.split(',')
        if colors:
            if q:
                q = q | Q(color__id__in=colors.split(','))
            else:
                q = Q(manufactory__id__in=restaurants.split(','))
#             kwargs['color__id__in'] = colors.split(',')

            
        manufactory_id = req.GET.get('manufactory_id')
        category_id = req.GET.get('category_id')
        
#         if keyword:
#             products = Product.objects.filter(Q(title__icontains=keyword)
#                                             |Q(description__icontains=keyword)
#                                             #|Q(manufactory__name__icontains=keyword)
#                                             |Q(year=keyword)).annotate(n_likes=Count('favoriteproduct'))
#         
        if manufactory_id:
            products = Product.objects.filter(manufactory_id=manufactory_id).annotate(n_likes=Count('favoriteproduct'))
        elif category_id:
            products = Product.objects.filter(category_id=category_id).annotate(n_likes=Count('favoriteproduct'))
        elif cats or restaurants or colors:
            if keyword:
                products = Product.objects.filter(q).filter(Q(name__icontains=keyword)
                                                  |Q(categories__name__icontains=keyword)
                                                  |Q(manufactory__name__icontains=keyword)
                                                  |Q(color__name__icontains=keyword))
            else:
                products = Product.objects.filter(q)
        else:
            if keyword:
                products = Product.objects.filter(Q(name__icontains=keyword)
                                                  |Q(categories__name__icontains=keyword)
                                                  |Q(manufactory__name__icontains=keyword)
                                                  |Q(color__name__icontains=keyword))
            else:
                products = Product.objects.filter().annotate(n_likes=Count('favoriteproduct'))

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
        return JsonResponse({'data':to_json(products)})
    
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
        items = Picture.objects.filter(product_id=product.id)
        ps = []
        for item in items:
            ps.append(to_json(item))
 
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
        if data and data['username']=='admin':
            
            # try:
            #     color = Color.objects.get(id=req.POST.get('color_id'))
            # except:
            #     color = None
            try:
                manufactory = Restaurant.objects.get(id=req.POST.get('manufactory_id'))
            except:
                manufactory = None
                
            _id = params.get('id')
            
            if _id: # For edit
                item = Product.objects.get(id=_id)
            else:                    
                item = Product()

            item.name = params.get('name')
            item.description = params.get('description')
            item.year = params.get('year')
            item.dimension = params.get('dimension')
            item.price = params.get('price')
            item.currency = params.get('currency')
            # item.color = color
            item.manufactory = manufactory
            #item.category = category

            item.save()
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
                
            self.processPictures(item, pictures)
            
            # select default picture
            pics = Picture.objects.filter(product_id=item.id)
            item.fpath = self.getDefaultPicture(pics)
            item.save()

            return JsonResponse({'tokenValid': True,'data':to_json(item)})
        return JsonResponse({'tokenValid':False, 'data':''})

    def processPictures(self, product, pictures):
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
                    self.rmPicture(pic)
                elif picture['status'] == 'changed':
                    self.savePicture(product, pic, picture)
                    pic.save()
            else:# new
                pic = Picture()
                self.savePicture(product, pic, picture)
        
        if reindex:
            self.reindexPicture(product.id)
    
    def savePicture(self, product, pic, picture):
        # product --- Product model object
        # pic --- Picture model object
        # picture --- dict from front end
        pic.index = picture['index']
        pic.name = picture['name']
        pic.product = product
        pic.image.save(picture['image'].name, picture['image'].file, True)
        pic.save()
                    
    def getDefaultPicture(self, pictures):
        if pictures.count() == 0:
            return ''
        else:
            if pictures.count()>0 and pictures[0].image.name:
                return pictures[0].image.name
            else:
                return ''

    def rmPicture(self, pic):
        try:
            os.remove(pic.image.path)
        except:
            print('remove image failed')
        pic.image.delete()
        pic.delete()
    
    def reindexPicture(self, pid):
        # pid --- product id
        pics = Picture.objects.filter(product_id=pid).order_by('index')
        i = 0
        for pic in pics:   
            pic.index = i
            i = i + 1
            pic.save()
            
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
        d = json.loads(req.body)
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
        
