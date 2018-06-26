# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import logging
import base64

from datetime import datetime

from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.exceptions import ObjectDoesNotExist#EmptyResultSet, MultipleObjectsReturned
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth import authenticate, login, get_user_model
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.conf import settings

from commerce.models import Restaurant
from account.models import Province, City, Address
from utils import to_json, create_jwt_token, get_data_from_token

ERR_USER_EXIST = 1
ERR_USER_DUPLICATED = 2
ERR_SAVE_USER_EXCEPTION = 3
ERR_USER_NOT_EXIST = 4
ERR_INVALID_EMAIL = 5

DEFAULT_PORTRAIT='assets/portrait.png'

logger = logging.getLogger(__name__)

def save_user(username, email, password, utype, firstname='', lastname='', portrait=''):
    user = None
    try:
        user = get_user_model().objects.create_user(username, email=email, password=password, type=utype)
        user.first_name=firstname
        user.last_name=lastname
        user.type = utype
        user.portrait = portrait
        user.save()
    except Exception as e:
        logger.error('Create user Exception: %s'%e)
    return user

@method_decorator(csrf_exempt, name='dispatch')
class ProvinceView(View):
    def getList(self):
        ps = []
        try:
            ps = Province.objects.all()#.annotate(n_products=Count('product'))
        except Exception as e:
            logger.error('Get provinces Exception:%s'%e)
            return JsonResponse({'data':[]})
        return JsonResponse({'data': to_json(ps)})
    
    def get(self, req, *args, **kwargs):
        pid = req.GET.get('id')
        if pid:
            pid = int(pid)
            try:
                item = Province.objects.get(id=pid)
                return JsonResponse({'data':to_json(item)})
            except Exception as e:
                print(e.message);
                return JsonResponse({'data':''})
        else:
            return self.getList()

@method_decorator(csrf_exempt, name='dispatch')
class CityView(View):
    def getList(self, province_id=None):
        cs = []
        
        try:
            if province_id:
                cs = City.objects.filter(province_id=province_id)
            else:
                cs = City.objects.all()#.annotate(n_products=Count('product'))
        except Exception as e:
            logger.error('Get address Exception:%s'%e)
            return JsonResponse({'data':[]})
        return JsonResponse({'data': to_json(cs)})
    
    def get(self, req, *args, **kwargs):
        pid = req.GET.get('province_id')
        cid = req.GET.get('id')
        if cid:
            cid = int(cid)
            try:
                item = City.objects.get(id=cid)
                return JsonResponse({'data':to_json(item)})
            except Exception as e:
                print(e.message);
                return JsonResponse({'data':''})
        elif pid:
            return self.getList(pid)
        else:
            return self.getList()

@method_decorator(csrf_exempt, name='dispatch')
class AddressView(View):
    def getList(self):
        addrs = []
        try:
            addrs = Address.objects.all()#.annotate(n_products=Count('product'))
        except Exception as e:
            logger.error('Get address Exception:%s'%e)
            return JsonResponse({'data':[]})
        return JsonResponse({'data': to_json(addrs)})
    
    def get(self, req, *args, **kwargs):
        pid = kwargs.get('id')
        if pid:
            pid = int(pid)
            try:
                item = Address.objects.get(id=pid)
                return JsonResponse({'data':to_json(item)})
            except Exception as e:
                print(e.message);
                return JsonResponse({'data':''})
        else:
            return self.getList()
        
    def delete(self, req, *args, **kwargs):
        pid = int(kwargs.get('id'))
        if pid:
            instance = Address.objects.get(id=pid)
            instance.delete()
            items = Address.objects.filter().order_by('-updated')
            return JsonResponse({'data':to_json(items)})
        return JsonResponse({'data':[]})
    
    def post(self, req, *args, **kwargs):
        ubody = req.body.decode('utf-8')
        params = json.loads(ubody)

        _id = params.get('id')
        if _id:
            item = Address.objects.get(id=_id)
        else:                    
            item = Address()
            
        item.street = params.get('street')
        province_id = params.get('province_id')
        city_id = params.get('city_id')
        try:
            item.province = Province.objects.get(id=province_id)
            item.city = City.objects.get(id=city_id)
        except Exception as e:
            print(e.message)
        
        item.save()
        return JsonResponse({'data':to_json(item)})
    
@method_decorator(csrf_exempt, name='dispatch')
class SignupView(View):
    def post(self, req, *args, **kwargs):
        """ sign up"""
        user = None
        ubody = req.body.decode('utf-8')
        d = json.loads(ubody)
        if d:
            username = d.get('username')
            email = d.get('email')
            password = d.get('password')
            utype = d.get('type')
        else:
            return JsonResponse({'token':'', 'user':''})

        r = None
        try:
            r = get_user_model().objects.get(email__iexact=email)
        except Exception:
            pass
        
        if r:
            return JsonResponse({'token':'', 'user':''})
        else: # username, email must have value
            user = save_user(username, email, password, utype)
            if user is not None:
                obj = {'username':username, 'email':email, 'type':utype, 'password':'',
                       'first_name':'', 'last_name':'', 'portrait':'' }
                token = create_jwt_token(obj);
                return JsonResponse({'token':token, 'data':obj})
            else:
                return JsonResponse({'token':'', 'data':''})
        
@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, req, *args, **kwargs):
        """ login"""
        ubody = req.body.decode('utf-8')
        d = json.loads(ubody)
        password = None
        r = None
        
        if d:
            password = d.get('password')
            account = d.get('account')

        if account and password:
            try:
                r = get_user_model().objects.get(Q(username__iexact=account) | Q(email__iexact=account))
            except Exception as e:  # models.DoesNotExist:
                logger.error('%s LoginView get user exception:%s'%(datetime.now(), e))
        
            if r and r.check_password(password):
                user = authenticate(req, username=r.username, password=password)
                if user is not None:
                    login(req, user) # make use of django session
                    
                if r.type == 'business':
                    restaurant = Restaurant.objects.get(admin_id=r.id)
                    token = create_jwt_token({'id':r.id, 'username':r.username, 'type':r.type,'restaurant_id':restaurant.id});
                else:
                    token = create_jwt_token({'id':r.id, 'username':r.username, 'type':r.type});
                    
                r.password = ''
                data = to_json(r)
                if r.type == 'business':
                    data['restaurant_id'] = restaurant.id 
                return JsonResponse({'token':token, 'data':data})
            else:
                return JsonResponse({'token':'', 'data':''})
        else:
            return JsonResponse({'token':'', 'data':''})

@method_decorator(csrf_exempt, name='dispatch')
class TokenView(View):
    def get(self, req, *args, **kwargs):
        authorizaion = req.META['HTTP_AUTHORIZATION']
        token = authorizaion.replace("Bearer ", "")
        data = get_data_from_token(token)
        if data:
            return JsonResponse({'data':data})
        else:
            return JsonResponse({'data':''})

    def post(self, req, *args, **kwargs):
        authorizaion = req.META['HTTP_AUTHORIZATION']
        token = authorizaion.replace("Bearer ", "")
        data = get_data_from_token(token)
        if data:
            return JsonResponse({'data':data})
        else:
            return JsonResponse({'data':''})
            
@method_decorator(csrf_exempt, name='dispatch')
class UserListView(View):
    def get(self, req, *args, **kwargs):
        authorizaion = req.META['HTTP_AUTHORIZATION']
        token = authorizaion.replace("Bearer ", "")
        data = get_data_from_token(token)
        if data:
            users = []
            try:
                users = get_user_model().objects.all()
            except Exception as e:
                logger.error('%s UserView get exception:%s'%(datetime.now(), e))
    
            return JsonResponse({'data':to_json(users)})
        else:
            return JsonResponse({'data':''})
        
@method_decorator(csrf_exempt, name='dispatch')
class UserFormView(View):
    def get(self, req, *args, **kwargs):
        if get_data_from_token(req):
            _id = int(kwargs.get('id'));
            user = None
            try:
                if _id:
                    user = get_user_model().objects.get(id=_id)
            except Exception as e:
                logger.error('%s UserFormView get exception:%s'%(datetime.now(), e))
    
            if user:
                return JsonResponse({'data':to_json(user)})
        return JsonResponse({'data':''})
                
@method_decorator(csrf_exempt, name='dispatch')
class UserView(View):
    # def get(self, req, *args, **kwargs):
    #     """ Find user by email
    #     """
    #     email = req.GET.get('email')
    #     users = None
    #     s = []
    #     if email:
    #         try:
    #             users = get_user_model().objects.filter(email__iexact=email)
    #         except Exception as e:
    #             logger.error('%s UserView get user exception:%s'%(datetime.now(), e))

    #         if users:
    #             for user in users:
    #                 s.append(user.to_json())
    #         return JsonResponse({'users':s})
    #     else:
    #         return JsonResponse({'users':[]})

    def get_user(self, d):
        """  Find user by query object
                d --- json object { source, email, username }
        """
        r = None
        _id = d.get('id')
        source = d.get('source')
        username = d.get('username')
        email = d.get('email')

        if id:
            try:
                r = get_user_model().objects.get(id=_id)
            except Exception as e:  # models.DoesNotExist:
                logger.info('%s UserView get user exception:%s'%(datetime.now(), e))
            return r

        try:
            r = get_user_model().objects.get(Q(username__iexact=username) | Q(email__iexact=email) & Q(source_iexact=source))
        except Exception as e:  # models.DoesNotExist:
            logger.info('%s UserView get user exception:%s'%(datetime.now(), e))

        return r

    def post(self, req, *args, **kwargs):
        """ sign up
        """
        user = None
        ubody = req.body.decode('utf-8')
        d = json.loads(ubody)
        if d:
            username = d.get('username')
            email = d.get('email')
            password = d.get('password')
            firstname = d.get('firstname')
            lastname = d.get('lastname')
            utype = d.get('type')
            portrait = d.get('portrait')
        else:
            return JsonResponse({'token':'', 'user':'', 'errors':[ERR_SAVE_USER_EXCEPTION]})

        r = None
        try:
            r = get_user_model().objects.get(email__iexact=email)
        except Exception as e:  # models.DoesNotExist:
            logger.info('%s UserView get user exception:%s'%(datetime.now(), e))

        if r:
            return JsonResponse({'token':'', 'user':'', 'errors':[ERR_USER_EXIST]})
        else: # assume username, email alwayse have value
            user = save_user(username, email, password, utype, firstname, lastname, portrait)
            if user is not None:
                user.password = ''
                obj = {'username':username, 'email':email, 'type':utype, 'password':'',
                       'first_name':'', 'last_name':'', 'portrait':'' }
                token = create_jwt_token(obj);
                return JsonResponse({'token':token, 'user':to_json(user), 'errors':[]})
            else:
                return JsonResponse({'token':'', 'user':'', 'errors':[ERR_SAVE_USER_EXCEPTION]})

    # def send_active_email(self, token, to_email):
    #     try:
    #         subject, from_email = settings.ACTIVE_EMAIL_SUBJECT, settings.EMAIL_ADDRESS
    #         text_content = 'Thank you for creating a new account. Please click on the link to active your account.'
    #         html_content = '<p>谢谢您注册像罔。请点击链接激活您的账号：<a href="'+settings.WEB_URL+'/#/activeAccount?token='+token+'">http://yocomput.com/active=IW3454HEUU34JUE84774HR74H83H3H</a></p>'
    #         msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    #         msg.attach_alternative(html_content, "text/html")
    #         msg.send()
    #     except Exception as e:
    #         print('send active email error:'+e)


@method_decorator(csrf_exempt, name='dispatch')
class InstitutionView(View):
    def post(self, req, *args, **kwargs):
        '''Institution sign up'''
        params = req.POST                 
        
        user = None
        username = params.get('username')
        email = params.get('email')
        password = params.get('password')
        firstname = 'me'#params.get('firstname')
        lastname = 'me'#params.get('lastname')
        utype = 'business'#params.get('type')
        portrait = ''#params.get('portrait')
        r = None
        try:
            r = get_user_model().objects.get(email__iexact=email)
        except Exception:  # models.DoesNotExist:
            pass
        
        if r:
            return JsonResponse({'token':'', 'user':'', 'errors':[ERR_USER_EXIST]})
        else: # assume username, email alwayse have value
            
            if params.get('lat') and params.get('lng'):
                user = save_user(username, email, password, utype, firstname, lastname, portrait)
                if user is not None:
                    image  = req.FILES.get("image")
                    restaurant = self.createRestaurant(params, image, user)
                    
                    obj = {'username':username, 'email':email, 'password':'', 'type':utype, 'password':'',
                           'first_name':'', 'last_name':'', 'portrait':'', 'restaurant_id':restaurant.id }
                    token = create_jwt_token(obj);
                    return JsonResponse({'token':token, 'user':to_json(user), 'errors':[]})
            return JsonResponse({'token':'', 'user':'', 'errors':[ERR_SAVE_USER_EXCEPTION]})
        
    def createRestaurant(self, params, image, user):
        item = Restaurant()                
        item.name = params.get('restaurant')
        item.description = ''#params.get('description')
        item.lat = float(params.get('lat'))
        item.lng = float(params.get('lng'))
        item.admin = user
        item.address = self.createAddress(params)
        item.save()
        if image:        
            item.image.save(image.name, image.file, True)
        item.save()
        #return JsonResponse({'data':to_json(item)})
        return item
    
    def createAddress(self, params):
        address = Address()
        address.street = params.get('street')
        address.sub_locality = params.get('sub_locality')
        address.postal_code = params.get('postal_code')
        address.lat = params.get('lat')
        address.lng = params.get('lng')
        address.province = params.get('province')
        address.city = params.get('city')
#         try:
#             address.province = Province.objects.get(name=province)
#             address.city = City.objects.get(name=city)
#         except:
#             pass
        address.save()
        return address


#             if utype == 'business':
#                 restaurant = d.get('restaurant')
#                 addr = d.get('address')
#                 category = d.get('category')
#                 lat = addr.lat
#                 lng = addr.lng
                
                #self.save_restaurant(restaurant, '', addr, image, lat, lng)

@method_decorator(csrf_exempt, name='dispatch')
class ProfileView(View):
    def get(self, req, *args, **kwargs):
        user_id = req.GET.get('user_id')
        if user_id:
#             try:
#                 profile = Profile.objects.get(user_id=user_id)
#                 return JsonResponse({'profile':profile.to_json()})
#             except Exception as e:
#                 logger.error('%s ProfileView get exception:%s'%(datetime.now(), e))
            return JsonResponse({'profile':None})
        else:
            return JsonResponse({'profile':None})

    def post(self, req, *args, **kwargs):
        ''' req.body must have {user_id, description, phone, street, unit, province_id, city_id, portrait}
        '''
        profile = None
        ubody = req.body.decode('utf-8')
        p = json.loads(ubody)
        
#         v = decode_jwt_token(p["token"])
#         if v is None:
#             return JsonResponse({'profile': None, 'error':'Invalid token'})    
#         else:

        if p:
            profile_id = p.get("id")
            if profile_id:
#                 try:
#                     profile = Profile.objects.get(id=profile_id)
#                 except ObjectDoesNotExist as e:
#                     logger.info('%s ProfileView get profile exception:%s'%(datetime.now(), e))
#                     return JsonResponse({'profile': None,'error':'Profile does not exist'})
#                 profile = self.save_profile(profile, profile.address, p)
                return JsonResponse({'profile': profile.to_json(),'error':None})
            else:
                user_id = p.get("user_id")
#                 if user_id:
#                     try:
#                         profile = Profile.objects.get(user_id=user_id)
#                     except ObjectDoesNotExist as e:
#                         logger.info('%s ProfileView get profile exception:%s'%(datetime.now(), e))
#                 
#                     if profile is None:
#                         profile = Profile()
#                         addr = Address()
#                         profile = self.save_profile(profile, addr, p)
#                     else:
#                         profile = self.save_profile(profile, profile.address, p)
                
                return JsonResponse({'profile': profile.to_json(),'error':None})
        
        return JsonResponse({'profile': None,'error':'Profile miss params'})        


    def save_profile(self, profile, addr, p):
        """ Create or update profile
            profile --- Profile Model object
            addr --- Address Model object
            p --- profile json object
        """
        profile.description = p.get("description")
        profile.phone = p.get("phone")
        profile.address = self.save_address(addr, p)
        user = None
        uid = p.get("user_id")
        if uid:
            try:
                user = get_user_model().objects.get(id=uid)
            except Exception as e:
                logger.info('Save profile get user exception:%s'%e)

        profile.user = user

        portrait_path = p.get("portrait")
        fpath = os.path.join('portraits', profile.user.username, portrait_path)

        full_fPath = os.path.join(settings.MEDIA_ROOT,fpath)
        if os.path.exists(full_fPath):
            profile.portrait = fpath

        profile.save()
        return profile


    def save_address(self, addr, p):
        """ Create or Update address with profile json values
            addr --- Address Model object
            p --- profile json object
        """
        province_id = p.get('province_id')
        city_id = p.get('city_id')
        province = None
        city = None

#         if province_id:
#             try:
#                 province = Province.objects.get(id=province_id)
#             except Exception:
#                 pass
# 
#         if city_id:
#             try:
#                 city = City.objects.get(id=city_id)
#             except Exception:
#                 pass
# 
#         addr.province = province
#         addr.city = city
#         addr.street = p.get('street')
#         addr.unit = p.get('unit')
#         addr.save()
        return addr

@method_decorator(csrf_exempt, name='dispatch')
class PortraitView(View):
    def get(self, req, *args, **kwargs):
        user_id = req.GET.get('user_id')
#         if user_id:
#             profile = None
#             try:
#                 profile = Profile.objects.get(user_id=user_id)
#             except Exception as e:
#                 logger.error('%s PortraitView get exception:%s'%(datetime.now(), e))
#             if profile:
#                 return JsonResponse({'profile':profile.to_json()})
        return JsonResponse({'profile':None})

    def post(self, req, *args, **kwargs):
        user_id = req.POST.get("user_id")
        file = req.FILES.get('file')
        if user_id and file:
            self.remove_portrait(user_id)
            fpath = self.save_portrait(user_id, file)
            return JsonResponse({'portrait': fpath}) 
        else:
            return JsonResponse({'portrait': None})

    def remove_portrait(self, user_id):
        profile = None
#         try:
#             profile = Profile.objects.get(user_id=user_id)
#         except Exception as e:
#             logger.info('%s PortraitView get profile exception:%s'%(datetime.now(), e))
#         if profile:
#             if profile.portrait.lower() != DEFAULT_PORTRAIT:
#                 fpath = os.path.join(settings.MEDIA_ROOT, profile.portrait)
#                 if os.path.exists(fpath):
#                     os.remove(fpath)

    def save_portrait(self, user_id, file):
        fpath = os.path.join(settings.MEDIA_ROOT, 'portraits')
        fname, ext = os.path.splitext(file.name)
        if not os.path.exists(fpath):
            os.makedirs(fpath)

        full_filename = os.path.join(fpath, user_id + ext)
        if os.path.exists(full_filename):
            os.remove(full_filename)
        
        fout = open(full_filename, 'wb+')
        fout.write(file.read())
        fout.close()
        return full_filename

@method_decorator(csrf_exempt, name='dispatch')
class ForgetPasswordView(View):
    #------------------------------------
    # Forget password
    def post(self, req):
        ubody = req.body.decode('utf-8')
        d = json.loads(ubody)
        from_email = settings.EMAIL_ADDRESS
        if 'email' in d:
            to_email = d['email']
    
            try:
                user = get_user_model().objects.get(email = to_email)
            except Exception as e:
                logger.error('Get user exception:%s'%e)
                return JsonResponse({'errors':[ERR_USER_NOT_EXIST]})
            
            password = get_user_model().objects.make_random_password()
            self.send_temp_password_email(from_email, to_email, password)
            
            try:
                user.set_password(password)
                user.save()
                return JsonResponse({'errors':[]})
            except Exception as e:
                logger.error('set password exception:%s'%e)
                return JsonResponse({'errors':[ERR_SAVE_USER_EXCEPTION]})
        else:
            return JsonResponse({'errors':[ERR_INVALID_EMAIL]})
        
    def send_temp_password_email(self, from_email, to_email, password):
        subject = "Your password has changed"
        body = "A temporary password has been sent to your email address. You will then be able to log in and change your password.\nYour new password: %s"%password
        try:
            send_mail(subject, body, from_email, [to_email])
        except Exception as e:
            logger.error('Send temporary password exception:%s'%e)

@method_decorator(csrf_exempt, name='dispatch')
class ChangePasswordView(View):
    #------------------------------------
    # change password
    def post(self, req, *args, **kwargs):
        ubody = req.body.decode('utf-8')
        d = json.loads(ubody)

        if 'user_id' in d and 'old_password' in d and 'password' in d:
            try:
                user = get_user_model().objects.get(id=d['user_id'])
            except Exception as e:
                return JsonResponse({'errors':[ERR_USER_NOT_EXIST]})

            if user.check_password(d['old_password']):
                user.set_password(d['password'])
    
                try:
                    user.save()
                except Exception as e:
                    logger.error('Change password exception:%s'% e)
                    return JsonResponse({'errors':[ERR_SAVE_USER_EXCEPTION]})
    
                return JsonResponse({'errors':[]})
            else:
                return JsonResponse({'errors':[ERR_USER_NOT_EXIST]})
        else:
            return JsonResponse({'errors':[ERR_USER_NOT_EXIST]})
        

@method_decorator(csrf_exempt, name='dispatch')
class ContactUsView(View):
    def post(self, req, *args, **kwargs):
        ubody = req.body.decode('utf-8')
        d = json.loads(ubody)
        name=d['name']
        from_email=d['email']
        phone=d['phone']
        message=d['message']
        
#         feedback = Feedback();
#         feedback.name = name;
#         feedback.email = from_email;
#         feedback.phone = phone;
#         feedback.message = message;
#         feedback.save();
        
        to_email = settings.EMAIL_ADDRESS  
#         to_email = "yajing.cheng12@gmail.com"
        subject = settings.SEND_EMAIL_SUBJECT
        text_content = 'Thank you for contacting us.'
        try:
            html_content = '<p>客户名称：'+name+'</p>'+'<p>客户电话：'+phone+'</p>'+'<p>发送信息：'+message+'</p>';
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()  
            return JsonResponse({'send':'0'})
        except Exception as e:
            logger.error('Failed to send email: '+ str(e))
            return JsonResponse({'send':''})
