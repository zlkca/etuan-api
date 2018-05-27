from django.db import models
from django.db.models import CharField, Model, ForeignKey, DateTimeField, DateField, DecimalField, IntegerField, ImageField, BooleanField
from django.conf import settings

# Create your models here.
class Post(Model):
	title = CharField(max_length=200, null=True, blank=True)
	body = CharField(max_length=1000, null=True, blank=True)
	
	author = ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, db_column='author_id', on_delete=models.CASCADE)
	created = DateTimeField(auto_now_add=True)
	updated = DateTimeField(auto_now=True)
	
	def __str__(self):
		return self.title + '_' + str(self.created)

class Comment(Model):
	body = CharField(max_length=500, null=True, blank=True)
	author = ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, db_column='author_id', on_delete=models.CASCADE)
	post = ForeignKey(Post, null=True, blank=True, db_column='post_id', on_delete=models.CASCADE)
	created = DateTimeField(auto_now_add=True)
	updated = DateTimeField(auto_now=True)
	
	def __str__(self):
		return self.author.username + ' re: ' + self.post.title
