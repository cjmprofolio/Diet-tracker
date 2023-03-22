from django.urls import path, include
from . import views
from .views import LoginUserView, Useregister
from django.contrib.auth.views import LogoutView 

app_name= 'members'

urlpatterns = [
    path('login/', LoginUserView.as_view(), name= 'login_user'),
    path('logout/', LogoutView.as_view(), name= 'logout_user'),
    path('register/', Useregister.as_view(), name= 'register'),
]