import jwt
import base64

from datetime import datetime, timedelta
from django.conf import settings
from django.db.models.query import QuerySet
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.db.models.fields.files import ImageField
from django.db.models.fields.reverse_related import ManyToOneRel


def obj_to_json(d, related_lookup=False):
    ''' d --- django Model class instance
    '''
    item = {}
    if d and d._meta:
        fields = d._meta.get_fields()
        for field in fields:
            key = field.name
            #print(type(field))
            if hasattr(d, key):
                v = getattr(d, key)
                if isinstance(field, ManyToOneRel) or key=='password': 
                    pass
                if isinstance(field, ManyToManyField):
                    item[key] = to_json(v.all())
                elif isinstance(field, ForeignKey):
                    if related_lookup:
                        item[key] = obj_to_json(v)
                    else:
                        if v and v.id:
                            item[key] = {'id': v.id }
                elif isinstance(field, ImageField):
                    #item[key] = v.name if v else None
                    if v and v.name:
                        item[key] = { 'data':v.name, 'file':'' }
                    else:
                        item[key] = { 'data':'', 'file':'' }
                else:
                    item[key] = v
    #     # version 1
    #     for k in d.__dict__.keys():
    #         if not '__' in k and not k.startswith('_'):
    #             v = getattr(d, k)
    #             if isinstance(v, ImageFieldFile):
    #                 item[k] = getattr(d, k).name if getattr(d, k) else None
    #             else: 
    #                 item[k] = getattr(d, k)
    return item

def to_json(a):
    if isinstance(a, QuerySet) and a.exists() or isinstance(a, list):
        r = []
        for d in a:
            item = obj_to_json(d, related_lookup=False)
            r.append(item)
        return r
    elif isinstance(a, QuerySet) and a.count()==0:
        return []
    else:
        return obj_to_json(a, related_lookup=True)


def create_jwt_token(obj):
    payload = {
        'data': obj,
        'expiry': str(datetime.utcnow() + timedelta(seconds=settings.JWT["EXPIRY"]))
    }
    return jwt.encode( payload, settings.JWT["SECRET"], algorithm=settings.JWT["ALGORITHM"])

def decode_jwt_token(token):
    try:
        return jwt.decode(token, settings.JWT["SECRET"], algorithms=[settings.JWT["ALGORITHM"]])
    except:
        return None

def get_data_from_token(token):
    if token:
        s = base64.b64decode(token).decode("utf-8").replace('"', '')
        payload = decode_jwt_token(s)
        if payload and payload['data']:
            return payload['data']
    return None        

