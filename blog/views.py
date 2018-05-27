import json
import os
import logging

from django.http import JsonResponse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from utils import to_json, get_data_from_token


from blog.models import Post, Comment

@method_decorator(csrf_exempt, name='dispatch')
class PostListView(View):
    def get(self, req, *args, **kwargs):
        try:
            items = Post.objects.all().order_by('-updated')
        except Exception as e:
            return JsonResponse({'data':[]})
        return JsonResponse({'data':to_json(items)})

@method_decorator(csrf_exempt, name='dispatch')
class PostView(View):
    def get(self, req, *args, **kwargs):
         _id = int(kwargs.get('id'))
         if _id:
             try:
                 item = Post.objects.get(id=_id)
                 return JsonResponse({'data':to_json(item)})
             except Exception as e:
                 return JsonResponse({'data':''})
         else:
             return JsonResponse({'data':''})

    def post(self, req, *args, **kwargs):
        params = json.loads(req.body)
        _id = params.get('id')
        if _id:
            item = Post.objects.get(id=_id)
        else:
            item = Post()

        item.title = params.get('title')
        item.body = params.get('body')
        author_id = params.get('author_id')
        try:
            item.author = settings.AUTH_USER_MODEL.objects.get(id=author_id)
        except:
            item.author = None
        item.created = params.get('created')
        item.updated = params.get('updated')
        item.save()
        return JsonResponse({'data':to_json(item)})

    def delete(self, req, *args, **kwargs):
        _id = int(kwargs.get('id'))
        if _id:
            try:
                item = Post.objects.get(id=_id)
                item.delete()
                items = Post.objects.all().order_by('-updated')
                return JsonResponse({'data':to_json(item)})
            except Exception as e:
                return JsonResponse({'data':''})
        else:
            return JsonResponse({'data':''})

@method_decorator(csrf_exempt, name='dispatch')
class CommentListView(View):
    def get(self, req, *args, **kwargs):
        try:
            items = Comment.objects.all().order_by('-updated')
        except Exception as e:
            return JsonResponse({'data':[]})
        return JsonResponse({'data':to_json(items)})

@method_decorator(csrf_exempt, name='dispatch')
class CommentView(View):
    def get(self, req, *args, **kwargs):
         _id = int(kwargs.get('id'))
         if _id:
             try:
                 item = Comment.objects.get(id=_id)
                 return JsonResponse({'data':to_json(item)})
             except Exception as e:
                 return JsonResponse({'data':''})
         else:
             return JsonResponse({'data':''})
    
    def post(self, req, *args, **kwargs):
         params = json.loads(req.body)
         _id = params.get('id')
         if _id:
             item = Comment.objects.get(id=_id)
         else:
             item = Comment()
    
         item.body = params.get('body')
         author_id = params.get('author_id')
         try:
             item.author = settings.AUTH_USER_MODEL.objects.get(id=author_id)
         except:
             item.author = None
         post_id = params.get('post_id')
         try:
             item.post = Post.objects.get(id=post_id)
         except:
             item.post = None
         item.created = params.get('created')
         item.updated = params.get('updated')
         item.save()
         return JsonResponse({'data':to_json(item)})

    def delete(self, req, *args, **kwargs):
         _id = int(kwargs.get('id'))
         if _id:
             try:
                 item = Comment.objects.get(id=_id)
                 item.delete()
                 items = Comment.objects.all().order_by('-updated')
                 return JsonResponse({'data':to_json(item)})
             except Exception as e:
                 return JsonResponse({'data':''})
         else:
             return JsonResponse({'data':''})

