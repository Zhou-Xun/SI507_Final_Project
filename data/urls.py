from django.urls import path
from . import views
from django.views.generic import TemplateView
app_name = 'data'

urlpatterns = [
    path('', views.HomeView.as_view(), name='all'),
    path('reddit', views.RedditListView.as_view(), name='reddit'),
    path('comment/<str:subid>', views.RedditCommentView.as_view(), name='comments'),
    path('twitter', views.TwitterListView.as_view(), name='twitter'),
]