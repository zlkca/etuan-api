from django.conf.urls import url
from blog.views import PostListView, PostView, CommentListView, CommentView

urlpatterns = [
    url('posts', PostListView.as_view()),
    url('post/(?P<id>[0-9]+)', PostView.as_view()),
    url('post', PostView.as_view()),
    url('comments', CommentListView.as_view()),
    url('comment/(?P<id>[0-9]+)', CommentView.as_view()),
    url('comment', CommentView.as_view()),
]