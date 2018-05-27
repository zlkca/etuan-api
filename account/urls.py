from django.conf.urls import url
from account.views import LoginView, TokenView, UserListView, UserFormView

urlpatterns = [
   url('login', LoginView.as_view()),
   url('token', TokenView.as_view()),
   url('users', UserListView.as_view()),
    url('user/(?P<id>[0-9]+)', UserFormView.as_view()),
    url('user', UserFormView.as_view())
]
