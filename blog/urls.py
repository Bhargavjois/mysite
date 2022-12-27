from . import views
from django.urls import path, re_path
from .feeds import LatestPostsFeed
from .views import UserPostsView, UpdatePostView, deletePost

urlpatterns = [
    path('',views.PostList, name='home'),
    path('add_post/',views.AddPostView,name='add_post'),
    path('user-posts/<str:usr>/',UserPostsView,name="user-posts"),
    path('post/edit/<str:slug>',UpdatePostView.as_view(),name="update_post"),
    path('editor/',views.PublishView,name='editor'),
    path('manage-users/',views.ManageUsersView,name='manage_users'),
    path("feed/rss", LatestPostsFeed(),name="post_feed"),
    path('about/',views.AboutView.as_view(),name='about'),
    path('profile/<str:usr>',views.profileView,name='profile'),
    path('our-authors/',views.AuthorsView,name="our-authors"),
    path('post-admin/',views.PaLandView.as_view(),name='pa-land'),
    path('contact/',views.ContactUs, name='contact'),
    path('policy/',views.PolicyView.as_view(), name='policy'),
    path('<slug:slug>/',views.post_detail, name='post_detail'),
    
]

htmx_urlpatterns = [
    path('delete_post/<str:slug>/',deletePost,name="delete-post"),
    path('like/<str:slug>',views.LikeView,name='like_post'),
    path('publish/<str:slug>',views.Publish,name='publish'),
    path('mkauth/<int:usr>',views.MakeAuthor,name="mkauthor"),
    path('mkedit/<int:usr>',views.MakeEditor,name="mkeditor"),
]

urlpatterns += htmx_urlpatterns