from django.conf.urls import url
from account.views import AddressView, LoginView, SignupView, InstitutionView, TokenView, UserListView, UserFormView

urlpatterns = [
    url('login', LoginView.as_view()),
    url('^signup', SignupView.as_view()),
    url('^institutionsignup', InstitutionView.as_view()),
    url('token', TokenView.as_view()),
    url('users', UserListView.as_view()),
    url('user/(?P<id>[0-9]+)', UserFormView.as_view()),
    url('user', UserFormView.as_view()),
    url('addresses', AddressView.as_view())
]
