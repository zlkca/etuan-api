from django.contrib import admin

from .models import Restaurant, Product, Picture, Category, Style, PriceRange
from .forms import CategoryForm, StyleForm
# 
# class ItemAdmin(admin.ModelAdmin):
# 	#fields = ('title', 'description')
# 	form = ItemForm

class CategoryAdmin(admin.ModelAdmin):
	#fields = ('title', 'description')
	form = CategoryForm

class StyleAdmin(admin.ModelAdmin):
	#fields = ('title', 'description')
	form = StyleForm

admin.site.register(Restaurant)
admin.site.register(Category,CategoryAdmin)
admin.site.register(Style, StyleAdmin)
admin.site.register(PriceRange)
admin.site.register(Product)
admin.site.register(Picture)
