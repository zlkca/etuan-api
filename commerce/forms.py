from django import forms
from commerce.models import Category, Style
# 
# class ItemForm(forms.ModelForm):
#     title = forms.CharField(max_length=250)
#     description = forms.CharField(max_length=1000, widget=forms.Textarea)
#     image = forms.ImageField(help_text="Max 5M")
# 
#     class Meta:
#         model = Item
#         fields = ['title', 'description', 'product', 'image']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        labels = {'name':'Category Name', 
        'description': 'Category Description'}

class StyleForm(forms.ModelForm):
    class Meta:
        model = Style
        fields = ['name', 'description']
        labels = {'name':'Style Name', 
        'description': 'Style Description'}


        
