""" URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.urls import include, path
from django.contrib import admin
from account.views import LoginView

urlpatterns = [
    path('api/', include('account.urls')),
    path('api/', include('commerce.urls')),
    path('api/', include('blog.urls')),
#   url('api/login', LoginView.as_view())
    #url(r'^api/login', LoginView.as_view()),
    # url(r'^api/users', UserView.as_view()),
    # url(r'^api/provinces', ProvinceView.as_view()),
    # url(r'^api/cities', CityView.as_view()),
    # url(r'^api/profiles', ProfileView.as_view()),
    # url(r'^api/portraits', PortraitView.as_view()),
    # url(r'^api/get-token', obtain_jwt_token),
    # url(r'^api/verify-token', verify_jwt_token), 
    # url(r'^api/forget-password', ForgetPasswordView.as_view()),
    # url(r'^api/change-password', ChangePasswordView.as_view()),
    # url(r'^api/businesses/(?P<bid>[0-9]+)', BusinessDetailView.as_view()),
    # url(r'^api/businesses', BusinessListView.as_view()),
    # url(r'^api/courses/(?P<bid>[0-9]+)', CourseDetailView.as_view()),
    # url(r'^api/courses', CourseListView.as_view()),

    # url(r'^api/posts', PostListView.as_view()),
    # url(r'^api/favorite-post', FavoritePostView.as_view()),
    # url(r'^api/carts', CartView.as_view()),
    # url(r'^api/cart-items', CartView.as_view()),
    # url(r'^api/contact', ContactUsView.as_view()),
    # url(r'^api/filters', ProductFilterView.as_view()),
    # url(r'^api/purchase', PaymentView.as_view())
]


from django.conf import settings
from django.views.static import serve

if settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
        # url(r'^users', AccountView.as_view())
    ]

if settings.ADMIN_ENABLED:
    urlpatterns +=  [
        url(r'^admin/', admin.site.urls),
    ]

admin.site.site_header = 'Administration'
admin.site.site_title = 'Administration'
