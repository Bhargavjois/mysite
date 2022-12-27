
"""from django.urls import path
from . import views
from .views import UserRegisterView"""
from django.urls import path, include, re_path
from members import views as user_view
from django.contrib.auth import views as auth_views
from members.views import ResetPasswordView

urlpatterns = [
    path('register/',user_view.register,name='register'),
    path('login/',user_view.usr_login,name='login'),
    path('change-password/', user_view.change_password, name='change_password'),
    path('logout/',user_view.logout_view,name='logout'),
    path('edit_user/<int:id>',user_view.edit_user_profile,name='edit-user'),
    path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),
]

htmx_urlpatterns = [
    path('check_username/',user_view.check_username,name="check-username"),
    path('check_email/',user_view.check_email,name="check-email"),
    path('deletedp/<int:uid>',user_view.deleteDp,name="deletedp"),
]

urlpatterns += htmx_urlpatterns