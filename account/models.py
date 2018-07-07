    # -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, Model, ForeignKey, DateTimeField, ImageField
from django.conf import settings
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _

STATUS = (('true','True'), ('false', 'False'))
USER_TYPES = (('member','Member'), ('business', 'Business'))

class Province(Model):
    name = CharField(max_length=64, null=True, blank = True)
    code = CharField(max_length=10, null=True, blank = True)
    country_code = CharField(max_length=10, null=True, blank = True)
    
    def __str__(self):
        return self.name
    
    def to_json(self):
        return {
            "id": self.id,
            "name": self.name
        }

class City(Model):
    name = CharField(max_length=64, null=True, blank = True)
    province = ForeignKey(Province, null=True, blank=True, db_column='province_id', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

class Address(Model):
    street = CharField(max_length=256, null=True, blank = True)
    unit = CharField(max_length=256, null=True, blank = True)
    postal_code = CharField(max_length=32, null=True, blank = True)
    sub_locality = CharField(max_length=32, null=True, blank = True)
    city = CharField(max_length=32, null=True, blank = True)#ForeignKey(City, null=True, blank=True, db_column='city_id', on_delete=models.CASCADE)
    province = CharField(max_length=32, null=True, blank = True)#ForeignKey(Province, null=True, blank=True, db_column='province_id', on_delete=models.CASCADE)
    lat = CharField(max_length=32, null=True, blank = True)
    lng = CharField(max_length=32, null=True, blank = True)

            
class User(AbstractUser):
    """ type --- 'user', 'business', 'super'
    """
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    portrait = CharField(max_length=256, null=True, blank=True) # main, google, facebook, wechat, qq, taobao
    type = CharField(max_length=16, choices=USER_TYPES, default='member')
        
def get_upload_image_path(instance, fpath):
    user_id = '0'
    if instance.user:
        user_id = instance.user.id
        fname, ext = os.path.splitext(fpath)
        return os.path.join('portraits', str(user_id) + ext)
    else:
        return '/assets/images/portrait.png'

class Profile(Model):
    gender = CharField(max_length=32, null=True, blank=True)
    description = CharField(max_length=255, null=True, blank=True)
    phone = CharField(max_length=64, null=True, blank=True)
    #portrait_path = CharField(max_length=255, null=True, blank=True)
    portrait = ImageField(upload_to=get_upload_image_path)
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = ForeignKey(Address, null=True, blank=True, db_column='address_id', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.username

class Feedback(Model):
    email = CharField(max_length=32, null=True, blank=True)
    phone = CharField(max_length=32, null=True, blank=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = CharField(max_length=255, null=True, blank=True)
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)
