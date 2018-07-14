from django.conf.urls import url
from commerce.views import ProductListView, ProductView, CategoryView, RestaurantView, OrderView

urlpatterns = [
    url('restaurants/(?P<id>[0-9]+)', RestaurantView.as_view()),
    url('restaurants', RestaurantView.as_view()),
    url('categories/(?P<id>[0-9]+)', CategoryView.as_view()),
    url('categories', CategoryView.as_view()),
    url('orders/(?P<id>[0-9]+)', OrderView.as_view()),
    url('orders', OrderView.as_view()),
    url('products', ProductListView.as_view()),
    url('product/(?P<id>[0-9]+)', ProductView.as_view()),
    url('product', ProductView.as_view())
]
